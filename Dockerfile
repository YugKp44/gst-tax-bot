# Use the official Python slim image
FROM python:3.10-slim

# Set a working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Tell Cloud Run which port to listen on
ENV PORT 8080

# Expose the port
EXPOSE 8080

# Start the app with Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--workers", "1"]
