# retrieve.py (final - returns top-1 clean result)

import pickle
import numpy as np
import re
from sentence_transformers import SentenceTransformer
import faiss

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

def clean_text(s: str) -> str:
    # Remove bullet characters and leading labels like "o A:", "Ans:", "Q:"
    s = re.sub(r"^[•*oO\-\d\.\(\)\s]*(Q\d*\.*|Q:|A:|Ans\.?)\s*", "", s, flags=re.IGNORECASE)
    # Remove repeated whitespace
    s = re.sub(r"\s+", " ", s)
    return s.strip()



def embed_query(query: str) -> np.ndarray:
    return model.encode([query], convert_to_numpy=True)

def search_faqs(query: str, k: int = 1):
    q_emb = embed_query(query)
    distances, indices = index.search(q_emb, k)

    seen = set()
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        faq = faqs[idx]
        q_text = faq["question"]
        if q_text in seen:
            continue
        seen.add(q_text)

        # Clean both question and answer
        question = clean_text(q_text)
        answer   = clean_text(faq["answer"])

        results.append({
            "question": question,
            "answer":   answer,
            "source":   faq.get("source", ""),
            "score":    float(dist)
        })
        if len(results) >= k:
            break

    return results

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
