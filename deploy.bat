@echo off
REM deploy.bat - Windows deployment script

echo 🚀 GST Tax Bot Deployment Script
echo ================================

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from template...
    copy .env.example .env
    echo ✅ Please edit .env file with your configuration
    exit /b 1
)

REM Check if embeddings exist
if not exist "embeddings\faiss.index" (
    echo ⚠️  Embeddings not found. Please run ingest.py first:
    echo    python ingest.py
    exit /b 1
)

echo 📦 Installing dependencies...
pip install -r requirements.txt

echo 🧪 Running tests...
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

echo 🎯 Starting deployment...
echo Choose your deployment platform:
echo 1) Local development
echo 2) Docker
echo 3) Railway
echo 4) Render

set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    echo 🛠️  Starting local development server...
    flask run --host=0.0.0.0 --port=8080
) else if "%choice%"=="2" (
    echo 🐳 Building Docker image...
    docker build -t gst-tax-bot .
    echo 🚀 Running Docker container...
    docker run -p 8080:8080 --env-file .env gst-tax-bot
) else if "%choice%"=="3" (
    echo 🚂 Deploying to Railway...
    echo Please visit: https://railway.app/new
    echo And connect your GitHub repository
) else if "%choice%"=="4" (
    echo 🎨 Deploying to Render...
    echo Please visit: https://render.com/new
    echo And connect your GitHub repository
) else (
    echo Invalid choice
    exit /b 1
)
