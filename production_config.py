# production_config.py - Production-optimized settings

import os

class ProductionConfig:
    """Production configuration for deployment"""
    
    # Use faster model for production
    MODEL_TIER = "balanced"  # flan-t5-base - good balance of speed and quality
    FAST_MODE = True        # Enable fast mode for production
    
    # Deployment settings
    PORT = int(os.environ.get("PORT", 8080))
    HOST = "0.0.0.0"
    DEBUG = False
    
    # Database settings
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/tax_data")
    
    # Performance settings
    GUNICORN_WORKERS = int(os.environ.get("WEB_CONCURRENCY", 2))
    GUNICORN_THREADS = int(os.environ.get("THREADS", 4))
    GUNICORN_TIMEOUT = int(os.environ.get("TIMEOUT", 120))
    
    # Cache settings
    ENABLE_CACHE = True
    CACHE_SIZE = 200  # Increased for production
    CACHE_TTL = 3600  # 1 hour
    
    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Environment detection
def is_production():
    """Check if running in production"""
    return os.environ.get("FLASK_ENV") == "production" or os.environ.get("RAILWAY_ENVIRONMENT_NAME") is not None or os.environ.get("RENDER") is not None

# Load config based on environment
if is_production():
    print("🚀 Loading PRODUCTION configuration")
    config = ProductionConfig()
else:
    print("🛠️  Loading DEVELOPMENT configuration")
    config = ProductionConfig()  # Use same config but with debug info
