# Use a specific Python 3.10 slim image as a base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for building Python packages
# and for git to clone any dependencies if needed.
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Upgrade pip and install the Python dependencies
# --no-cache-dir is used to reduce the image size
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-download and cache the models during the build process.
# This saves time on the first run of the container.
# Using a Python heredoc to execute the download script.
RUN python3 -c "from sentence_transformers import SentenceTransformer; from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; SentenceTransformer('all-MiniLM-L6-v2'); AutoTokenizer.from_pretrained('google/flan-t5-small'); AutoModelForSeq2SeqLM.from_pretrained('google/flan-t5-small')"

# Copy the rest of the application code into the container
COPY . .

# Expose the port Gunicorn will run on (matches the port used by Cloud Run)
EXPOSE 8080

# Command to run the application using Gunicorn
# -b binds the server to all network interfaces on port 8080
# --workers 1 is a safe default for a small app
# --timeout 120 gives a generous 2-minute timeout for requests
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app", "--workers", "1", "--timeout", "120"]
