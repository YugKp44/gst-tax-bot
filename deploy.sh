#!/bin/bash
# deploy.sh - Deployment script

echo "🚀 GST Tax Bot Deployment Script"
echo "================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "✅ Please edit .env file with your configuration"
    exit 1
fi

# Check if embeddings exist
if [ ! -f "embeddings/faiss.index" ]; then
    echo "⚠️  Embeddings not found. Please run ingest.py first:"
    echo "   python ingest.py"
    exit 1
fi

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🧪 Running tests..."
python -c "
try:
    from app import app
    from model import generator
    from retrieve import search_faqs
    print('✅ All modules loaded successfully')
except Exception as e:
    print(f'❌ Error loading modules: {e}')
    exit(1)
"

echo "🎯 Starting deployment..."
echo "Choose your deployment platform:"
echo "1) Local development"
echo "2) Docker"
echo "3) Railway"
echo "4) Render"

read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "🛠️  Starting local development server..."
        flask run --host=0.0.0.0 --port=8080
        ;;
    2)
        echo "🐳 Building Docker image..."
        docker build -t gst-tax-bot .
        echo "🚀 Running Docker container..."
        docker run -p 8080:8080 --env-file .env gst-tax-bot
        ;;
    3)
        echo "🚂 Deploying to Railway..."
        echo "Please visit: https://railway.app/new"
        echo "And connect your GitHub repository"
        ;;
    4)
        echo "🎨 Deploying to Render..."
        echo "Please visit: https://render.com/new"
        echo "And connect your GitHub repository"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
