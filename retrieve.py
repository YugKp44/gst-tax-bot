# retrieve.py - Enhanced retrieval with query processing

import pickle
import numpy as np
import re
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Dict, Optional
from query_processor import QueryProcessor

# Load once at startup
INDEX_PATH = "embeddings/faiss.index"
META_PATH  = "embeddings/faq_meta.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"

print("Loading FAISS index…")
index = faiss.read_index(INDEX_PATH)
print("Loading metadata…")
with open(META_PATH, "rb") as f:
    faqs = pickle.load(f)

print("Loading embedding model…")
model = SentenceTransformer(MODEL_NAME)

# Initialize query processor
query_processor = QueryProcessor()

def clean_text(s: str) -> str:
    # Remove bullet characters and leading labels like "o A:", "Ans:", "Q:"
    s = re.sub(r"^[•*oO\-\d\.\(\)\s]*(Q\d*\.*|Q:|A:|Ans\.?)\s*", "", s, flags=re.IGNORECASE)
    # Remove repeated whitespace
    s = re.sub(r"\s+", " ", s)
    return s.strip()



def embed_query(query: str) -> np.ndarray:
    return model.encode([query], convert_to_numpy=True)

def search_faqs(query: str, k: int = 3) -> List[Dict]:
    """Enhanced search with query processing and intent detection"""
    
    # Process query to detect intent and extract entities
    intent = query_processor.detect_intent(query)
    
    # Use processed query for initial search
    results = _search_with_query(intent.processed_query, k)
    
    # If results are poor, try expanded search
    if query_processor.should_expand_search(intent, results):
        related_queries = query_processor.generate_related_queries(intent)
        
        # Search with related queries and combine results
        all_results = results.copy()
        for related_query in related_queries:
            related_results = _search_with_query(related_query, k//2)
            all_results.extend(related_results)
        
        # Remove duplicates and re-rank
        seen_questions = set()
        unique_results = []
        for result in all_results:
            if result['question'] not in seen_questions:
                seen_questions.add(result['question'])
                unique_results.append(result)
        
        # Sort by relevance score and take top k
        unique_results.sort(key=lambda x: x['score'])
        results = unique_results[:k]
    
    # Add intent information to results
    for result in results:
        result['intent'] = intent.intent_type
        result['entities'] = intent.extracted_entities
    
    return results

def _search_with_query(query: str, k: int) -> List[Dict]:
    """Internal search function"""
    q_emb = embed_query(query)
    distances, indices = index.search(q_emb, min(k * 2, len(faqs)))  # Search more, filter later

    seen = set()
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx >= len(faqs):  # Safety check
            continue
            
        faq = faqs[idx]
        q_text = faq["question"]
        if q_text in seen:
            continue
        seen.add(q_text)

        # Clean both question and answer
        question = clean_text(q_text)
        answer   = clean_text(faq["answer"])

        # Additional relevance filtering
        relevance_score = _calculate_relevance(query, question, answer, float(dist))

        results.append({
            "question": question,
            "answer":   answer,
            "source":   faq.get("source", ""),
            "score":    relevance_score,
            "original_score": float(dist)
        })
        
        if len(results) >= k:
            break

    return results

def _calculate_relevance(query: str, question: str, answer: str, distance: float) -> float:
    """Calculate enhanced relevance score"""
    base_score = distance
    
    # Boost score for exact keyword matches
    query_words = set(query.lower().split())
    question_words = set(question.lower().split())
    answer_words = set(answer.lower().split())
    
    # Calculate keyword overlap
    question_overlap = len(query_words.intersection(question_words)) / max(len(query_words), 1)
    answer_overlap = len(query_words.intersection(answer_words)) / max(len(query_words), 1)
    
    # Apply boosts
    if question_overlap > 0.3:
        base_score *= 0.8  # Lower score is better
    if answer_overlap > 0.2:
        base_score *= 0.9
    
    # Penalty for very short answers (likely incomplete)
    if len(answer.split()) < 10:
        base_score *= 1.1
    
    return base_score

if __name__ == "__main__":
    while True:
        q = input("\nEnter your question (or 'exit'): ").strip()
        if q.lower() == "exit":
            break
        results = search_faqs(q, k=1)
        if not results:
            print("Sorry, I don’t have an answer for that.")
            continue
        res = results[0]
        print(f"\nQ: {res['question']}")
        print(f"A: {res['answer']}  [source: {res['source']}]")
