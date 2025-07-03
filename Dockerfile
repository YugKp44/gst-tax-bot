# ───────────── Dockerfile ─────────────
FROM python:3.10-slim

WORKDIR /app

# Install build tools for model caching
RUN apt-get update && apt-get install -y \
    build-essential cmake git && \
    rm -rf /var/lib/apt/lists/*

# Copy & install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-cache models at build time
RUN python3 - <<'EOF'
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
SentenceTransformer("all-MiniLM-L6-v2")               # embed model
AutoTokenizer.from_pretrained("google/flan-t5-small") # gen tokenizer
AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small") # gen model
EOF

# Copy application code & assets
COPY . .

# Expose Cloud Run port
EXPOSE 8080

# Launch via Gunicorn with generous timeout
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app", "--workers", "1", "--timeout", "120"]
