from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
from typing import List
import torch
import re
import hashlib
import time
from answer_enhancer import answer_enhancer
from model_config import ModelConfig, CURRENT_MODEL_TIER, FAST_MODE

# Simple response cache for faster repeated queries
response_cache = {}
CACHE_SIZE_LIMIT = 100

# Get model configuration
model_config = ModelConfig.get_config(CURRENT_MODEL_TIER)
MODEL_NAME = model_config["name"]

print(f"\n🚀 Model Configuration:")
print(f"   Tier: {CURRENT_MODEL_TIER}")
print(f"   Model: {MODEL_NAME}")
print(f"   Size: {model_config['size']}")
print(f"   Speed: {model_config['speed']}")
print(f"   Fast Mode: {'Enabled' if FAST_MODE else 'Disabled'}")
print()

# ── Load model/tokenizer with optimizations ──
print(f"Loading model {MODEL_NAME}…")
device = 0 if torch.cuda.is_available() else -1
print(f"Device set to use: {'GPU' if device == 0 else 'CPU'}")

# Load with optimization for faster inference
load_params = ModelConfig.get_model_load_params(CURRENT_MODEL_TIER)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME, **load_params)

# If using GPU, move model to GPU
if torch.cuda.is_available() and load_params.get("device_map") is None:
    model = model.to('cuda')

# Get generation parameters based on configuration
gen_params = ModelConfig.get_generation_params(CURRENT_MODEL_TIER, FAST_MODE)
print(f"Generation params: max_tokens={gen_params['max_new_tokens']}, fast_mode={FAST_MODE}")

generator = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer,
    device=device,
    pad_token_id=tokenizer.eos_token_id,  # Avoid warnings
    **gen_params
)

# ── Enhanced Prompt Templates for Different Intents ──
PROMPT_TEMPLATES = {
    'gstin_lookup': """
You are an expert in Indian GST law and business information. The user is asking about GSTIN or business information. Provide comprehensive details including all available information about the business entity.

Context:
{contexts}

Question:
{query}

Please provide a detailed answer covering all relevant aspects:
""",
    'gst_rate': """
You are an expert in Indian GST rates and HSN codes. The user is asking about tax rates. Provide comprehensive information including:
- Current GST rates
- HSN/SAC codes if applicable
- Any exemptions or special conditions
- Examples where helpful

Context:
{contexts}

Question:
{query}

Detailed Answer:
""",
    'compliance': """
You are an expert in GST compliance and penalties. Provide comprehensive information including:
- Specific compliance requirements
- Important deadlines and due dates
- Penalties for non-compliance
- Step-by-step procedures where applicable

Context:
{contexts}

Question:
{query}

Comprehensive Answer:
""",
    'filing': """
You are an expert in GST return filing. Provide detailed step-by-step guidance including:
- Complete filing procedures
- Required documents
- Important deadlines
- Common mistakes to avoid

Context:
{contexts}

Question:
{query}

Step-by-step Answer:
""",
    'general': """
You are an expert in Indian GST and Income-Tax law. Provide a comprehensive and detailed answer using the context below. 

Instructions:
- Give complete explanations, not just brief summaries
- Include specific details, numbers, and examples where available
- Use bullet points for multiple items or steps
- Mention relevant legal sections or sources
- If the context provides multiple aspects, cover all of them

Context:
{contexts}

Question:
{query}

Comprehensive Answer:
"""
}

def generate_answer(query: str, contexts: List[dict]) -> str:
    # Check cache first for faster responses
    cache_key = _get_cache_key(query, contexts)
    if cache_key in response_cache:
        print("DEBUG: Cache hit! Returning cached response")
        return response_cache[cache_key]
    
    start_time = time.time()
    
    # Compose context from top matches with more detail
    ctx_parts = []
    for i, c in enumerate(contexts, 1):
        source_text = ', '.join(c['source']) if isinstance(c['source'], list) else c['source']
        ctx_parts.append(f"Context {i}:\nQ: {c['question']}\nA: {c['answer']}\nSource: {source_text}")
    
    ctx = "\n\n".join(ctx_parts)

    # Adjust context limit based on model tier
    context_limit = 4000 if CURRENT_MODEL_TIER == "fastest" else 6000
    if len(ctx) > context_limit:
        ctx = ctx[:context_limit] + "...\n[Note: Context truncated for processing]"

    # Select appropriate prompt template based on intent
    intent_type = contexts[0].get('intent', 'general') if contexts else 'general'
    template = PROMPT_TEMPLATES.get(intent_type, PROMPT_TEMPLATES['general'])
    
    prompt = template.format(contexts=ctx, query=query)
    
    # Debug: Log prompt and context info
    print(f"DEBUG: Context length: {len(ctx)} characters")
    print(f"DEBUG: Prompt length: {len(prompt)} characters")
    print(f"DEBUG: Intent type: {intent_type}")
    
    # Generate with configured parameters
    output = generator(prompt)
    
    answer = output[0]["generated_text"].strip()
    generation_time = time.time() - start_time
    
    print(f"DEBUG: Generation time: {generation_time:.2f}s")
    print(f"DEBUG: Raw model output length: {len(answer)} characters")
    if len(answer) > 200:
        print(f"DEBUG: Raw answer preview: {answer[:200]}...")
    else:
        print(f"DEBUG: Raw answer: {answer}")

    # Enhanced post-processing that preserves content
    answer = _post_process_answer(answer, intent_type, query)
    
    # Enhance short or incomplete answers (but not in fast mode)
    if not FAST_MODE and (len(answer.strip()) < 100 or len(answer.split()) < 15):
        answer = answer_enhancer.enhance_answer(answer, query, contexts)
    
    # Cache the response for future use
    _cache_response(cache_key, answer)
    
    total_time = time.time() - start_time
    print(f"DEBUG: Total processing time: {total_time:.2f}s")
    
    return answer

def _get_cache_key(query: str, contexts: List[dict]) -> str:
    """Generate a cache key from query and context"""
    key_data = query.lower().strip()
    if contexts:
        # Include first context's question for better cache matching
        key_data += "_" + contexts[0].get('question', '')[:100]
    return hashlib.md5(key_data.encode()).hexdigest()[:16]

def _cache_response(cache_key: str, response: str):
    """Cache a response with size limit"""
    global response_cache
    
    if len(response_cache) >= CACHE_SIZE_LIMIT:
        # Remove oldest entry (simple FIFO)
        oldest_key = next(iter(response_cache))
        del response_cache[oldest_key]
    
    response_cache[cache_key] = response

def _post_process_answer(answer: str, intent_type: str, original_query: str = "") -> str:
    """Enhanced post-processing that preserves content while improving formatting"""
    
    # If answer is too short, it might be incomplete - preserve it as is initially
    original_length = len(answer)
    
    # Fix markdown-style bullets but preserve content
    answer = answer.replace(" - ", "\n- ").replace("• ", "\n- ").replace("•", "\n- ")
    
    # Only remove redundant phrases if they don't contain important content
    # Be more conservative about removal
    redundant_patterns = [
        r'\b(?:as per the above context|according to the above information)\b',
        r'\b(?:based on the context provided)\b'
    ]
    
    for pattern in redundant_patterns:
        answer = re.sub(pattern, '', answer, flags=re.IGNORECASE)
    
    # Format specific to intent but don't remove content
    if intent_type == 'gst_rate':
        # Ensure percentages are clearly formatted
        answer = re.sub(r'(\d+(?:\.\d+)?)\s*percent', r'\1%', answer, flags=re.IGNORECASE)
        answer = re.sub(r'(\d+(?:\.\d+)?)\s*per\s*cent', r'\1%', answer, flags=re.IGNORECASE)
    
    # Clean up formatting but preserve all content
    answer = re.sub(r'\n\s*\n\s*\n+', '\n\n', answer)  # Max 2 consecutive newlines
    answer = re.sub(r'^\s+', '', answer, flags=re.MULTILINE)  # Remove leading spaces
    
    # If the processed answer became significantly shorter, it might have lost important content
    if len(answer) < original_length * 0.7 and original_length > 50:
        # Restore some of the original formatting but still clean it up
        answer = answer.replace(": -", ":\n\n- ")
    
    # Ensure minimum answer quality for common questions
    if len(answer.strip()) < 30 and any(term in original_query.lower() for term in ['what is', 'define', 'explain']):
        # The answer might be too brief, add a note
        if answer.strip():
            answer += "\n\n[Note: This is a brief summary. More detailed information may be available in the referenced sources.]"
    
    return answer.strip()

# ── CLI test ──
if __name__ == "__main__":
    from retrieve import search_faqs
    sample = "What is GSTR-1?"
    ctxs   = search_faqs(sample, k=2)
    print(generate_answer(sample, ctxs))
