# ──────────────── Dockerfile ────────────────
# Use the official Python slim image
FROM python:3.10-slim

# 1) Set working directory
WORKDIR /app

# 2) Install any build tools needed for dependencies
RUN apt-get update && apt-get install -y \
    build-essential cmake git && \
    rm -rf /var/lib/apt/lists/*

# 3) Copy & install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 4) Pre‑cache the retrieval & generation models at build time
RUN python3 - <<EOF
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Cache embedding model
SentenceTransformer("all-MiniLM-L6-v2")
# Cache text‑generation model
AutoTokenizer.from_pretrained("google/flan-t5-small")
AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
EOF

# 5) Copy your application code & assets
COPY . .

# 6) Expose port 8080 for Cloud Run
EXPOSE 8080

# 7) Start Gunicorn with a 120s timeout (first request may be slow)
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app", "--workers", "1", "--timeout", "120"]
