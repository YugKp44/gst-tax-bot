import os
import re
import logging
from flask import Flask, render_template, request, jsonify

# 1) Pre‑load everything once
from retrieve import search_faqs
from model    import generate_answer

app = Flask(__name__, template_folder="templates", static_folder="static")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

@app.route("/healthz")
def healthz():
    return "OK", 200

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

@app.route("/")
def home():
    try:
        return render_template("index.html")
    except Exception:
        logger.exception("Error rendering index.html")
        return "Internal Server Error", 500

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(force=True)
    q = data.get("question", "").strip()
    logger.info("Question: %s", q)

    contexts = search_faqs(q, k=3)
    if not contexts or contexts[0]["score"] > 1.0:
        answer = "This chatbot supports only GST/Income‑Tax queries."
        sources = []
    else:
        raw = generate_answer(q, contexts)
        cleaned = re.sub(r"\s*\([^)]+\)\s*$", "", raw).strip()
        answer = cleaned.replace(": -", ":\n\n- ")
        srcs = []
        for c in contexts:
            s = c["source"]
            srcs.extend(s if isinstance(s, list) else [s])
        sources = sorted(set(srcs))

    return jsonify(answer=answer, sources=sources)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
