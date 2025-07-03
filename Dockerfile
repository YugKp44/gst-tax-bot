# Use Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install build tools if needed
RUN apt-get update && apt-get install -y \
    build-essential cmake git && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .  
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre‑download and cache the SBERT & T5 models at build time
RUN python3 - <<EOF
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Cache the embeddings model
SentenceTransformer("all-MiniLM-L6-v2")
# Cache the generation model
AutoTokenizer.from_pretrained("google/flan-t5-small")
AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
EOF

# Copy your application code and assets
COPY . .

# Expose the port Cloud Run expects
EXPOSE 8080

# Start the app with Gunicorn, allow longer first‑request time
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app", "--workers", "1", "--timeout", "120"]
