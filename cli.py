# cli.py

from retrieve import search_faqs
from model   import generate_answer

if __name__ == "__main__":
    while True:
        q = input("\nAsk me about GST/IT (or 'exit'): ").strip()
        if q.lower() == "exit":
            break

        contexts = search_faqs(q, k=3)
        if not contexts:
            print("Sorry, I don’t have that in my knowledge base.")
            continue

        answer = generate_answer(q, contexts)
        print("\n" + answer)
