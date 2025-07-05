from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
from typing import List
import torch

MODEL_NAME = "google/flan-t5-base"

# ── Load model/tokenizer ──
print(f"Loading model {MODEL_NAME}…")
device = 0 if torch.cuda.is_available() else -1
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model     = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

generator = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer,
    device=device,
    max_new_tokens=256,
    do_sample=False,
)

# ── Prompt format ──
PROMPT_TEMPLATE = """
You are an expert in Indian GST and Income-Tax law. Use the context below to answer the question clearly and briefly. Use bullet points if the answer has multiple items. Mention sources where relevant.

Context:
{contexts}

Question:
{query}

Answer:
"""

def generate_answer(query: str, contexts: List[dict]) -> str:
    # Compose context from top matches
    ctx = "\n\n".join(
        f"Q: {c['question']}\nA: {c['answer']} (source: {', '.join(c['source']) if isinstance(c['source'], list) else c['source']})"
        for c in contexts
    )

    # Truncate context if needed (safe limit ~1800 tokens)
    if len(ctx) > 4000:
        ctx = ctx[:4000] + "..."

    prompt = PROMPT_TEMPLATE.format(contexts=ctx, query=query)
    output = generator(prompt)
    answer = output[0]["generated_text"].strip()

    # Fix markdown-style bullets
    answer = answer.replace(" - ", "\n- ").replace("• ", "\n- ").replace("•", "\n- ")
    return answer

# ── CLI test ──
if __name__ == "__main__":
    from retrieve import search_faqs
    sample = "What is GSTR-1?"
    ctxs   = search_faqs(sample, k=2)
    print(generate_answer(sample, ctxs))
