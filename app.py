from flask import Flask, render_template, request, jsonify
import re  # <-- Import the 're' module

# Assuming these are your custom modules
from retrieve import search_faqs
from model import generate_answer

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    q = data.get("question", "")

    # 1) Retrieval
    contexts = search_faqs(q, k=3)

    if not contexts or contexts[0]["score"] > 1.0:
        text = "This chatbot currently supports only GST and Income Tax queries. Please ask a question related to Indian taxation"
        sources = []
    else:
        raw = generate_answer(q, contexts)

        # --- MODIFICATION START ---
        # Remove the source text in parentheses (e.g., "(Source: ...)") from the end of the answer
        text_cleaned = re.sub(r'\s*\([^)]+\)$', '', raw).strip()
        # --- MODIFICATION END ---

        # Force-bullets newline on the cleaned text
        text = text_cleaned.replace(": -", ":\n\n- ")
        
        sources = sorted({s for c in contexts for s in (c["source"] if isinstance(c["source"], list) else [c["source"]])})

    return jsonify({"answer": text, "sources": sources})

if __name__ == "__main__":
    app.run(debug=True)