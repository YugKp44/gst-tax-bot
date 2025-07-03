import os
import re
import logging
from flask import Flask, render_template, request, jsonify

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# ── Configure logging ──
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger()

# ── Health check for Cloud Run readiness ──
@app.route("/healthz")
def healthz():
    return "OK", 200

# ── Home page ──
@app.route("/")
def home():
    try:
        return render_template("index.html")
    except Exception as e:
        # Log full stack trace
        logger.exception("Failed to render index.html")
        return "Internal Server Error", 500

# ── Main chatbot endpoint ──
@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json(force=True)
        q = data.get("question", "").strip()
        logger.info("Received question: %s", q)

        # Lazy‑load heavy modules
        from retrieve import search_faqs
        from model    import generate_answer

        # 1) Retrieval
        contexts = search_faqs(q, k=3)
        logger.debug("Retrieved %d contexts, top score=%.3f",
                     len(contexts),
                     contexts[0]["score"] if contexts else None)

        # 2) Fallback if no good match
        if not contexts or contexts[0]["score"] > 1.0:
            text = (
                "This chatbot currently supports only GST and "
                "Income Tax queries. Please ask a question related "
                "to Indian taxation."
            )
            sources = []
        else:
            # 3) Generate & clean answer
            raw = generate_answer(q, contexts)
            # Strip any trailing "(...source...)" 
            text_cleaned = re.sub(r"\s*\([^)]+\)\s*$", "", raw).strip()
            # Force bullet newlines
            text = text_cleaned.replace(": -", ":\n\n- ")
            # 4) Collect sources
            src_set = set()
            for c in contexts:
                src = c["source"]
                if isinstance(src, list):
                    src_set.update(src)
                else:
                    src_set.add(src)
            sources = sorted(src_set)

        logger.info("Responding with answer of length %d", len(text))
        return jsonify(answer=text, sources=sources)

    except Exception as e:
        # Catch-all for unexpected errors
        logger.exception("Error in /ask endpoint")
        return jsonify(
            answer="Internal server error. Please try again later.",
            sources=[]
        ), 500

# ── Entrypoint ──
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # default 8080 on Cloud Run
    logger.info("Starting Flask on port %d", port)
    app.run(host="0.0.0.0", port=port)
