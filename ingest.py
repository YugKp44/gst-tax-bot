import os
import json
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

def load_faqs(json_path="data/raw/faqs.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def embed_faqs(faqs, model_name="all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    texts = [faq["question"] + " " + faq["answer"] for faq in faqs]
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    return embeddings

def save_faiss_index(embeddings, index_path="embeddings/faiss.index"):
    dim = embeddings.shape[1]
    index = faiss.IndexHNSWFlat(dim, 32)
    index.add(embeddings)
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    faiss.write_index(index, index_path)
    return index

def save_metadata(faqs, path="embeddings/faq_meta.pkl"):
    with open(path, "wb") as f:
        pickle.dump(faqs, f)

def main():
    faqs = load_faqs()
    print(f"Loaded {len(faqs)} FAQs")
    embeddings = embed_faqs(faqs)
    print(f"Embeddings shape: {embeddings.shape}")
    save_faiss_index(embeddings)
    save_metadata(faqs)
    print("✅ FAISS index and metadata saved in 'embeddings/'")

if __name__ == "__main__":
    main()
