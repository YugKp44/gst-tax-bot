# 🚀 GST Tax Bot Deployment Guide

## Pre-deployment Checklist

### 1. Prepare Your Data
```bash
# Make sure you have your embeddings ready
python ingest.py
```

### 2. Set Up Environment Variables
```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your actual values:
# - MONGO_URI: Your MongoDB connection string
# - PORT: Port number (default: 8080)
```

### 3. Test Locally First
```bash
# Test the application
python -m flask run --port=8080

# Or use the deployment script
./deploy.bat  # Windows
./deploy.sh   # Linux/Mac
```

---

## Deployment Options

### 🎨 Option 1: Render (Recommended - Free Tier Available)

1. **Create a Render account**: Visit [render.com](https://render.com)

2. **Connect your GitHub repository**:
   - Push your code to GitHub first
   - In Render dashboard, click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure the service**:
   ```
   Name: gst-tax-bot
   Region: Choose closest to your users
   Branch: main
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --bind 0.0.0.0:$PORT app:app
   ```

4. **Set environment variables**:
   ```
   MONGO_URI=your_mongodb_connection_string
   PYTHON_VERSION=3.11.0
   ```

5. **Deploy**: Click "Create Web Service"

**Pros**: Free tier, automatic HTTPS, easy GitHub integration
**Cons**: Cold starts on free tier

---

### 🚂 Option 2: Railway (Fast & Simple)

1. **Create account**: Visit [railway.app](https://railway.app)

2. **Deploy from GitHub**:
   - Click "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Python and uses your existing configuration

3. **Set environment variables**:
   - Go to Variables tab
   - Add `MONGO_URI` with your MongoDB connection

4. **Deploy**: Automatic deployment starts

**Pros**: Very fast deployment, great for development
**Cons**: Limited free tier

---

### 🐳 Option 3: Docker (Any Platform)

1. **Build the image**:
   ```bash
   docker build -t gst-tax-bot .
   ```

2. **Run locally**:
   ```bash
   docker run -p 8080:8080 --env-file .env gst-tax-bot
   ```

3. **Deploy to any platform**:
   - Google Cloud Run
   - AWS ECS
   - Azure Container Instances
   - DigitalOcean App Platform

**Pros**: Works anywhere, consistent environment
**Cons**: Requires Docker knowledge

---

### ☁️ Option 4: Google Cloud Run

1. **Install Google Cloud SDK**

2. **Build and push**:
   ```bash
   gcloud builds submit --tag gcr.io/[PROJECT-ID]/gst-tax-bot
   ```

3. **Deploy**:
   ```bash
   gcloud run deploy --image gcr.io/[PROJECT-ID]/gst-tax-bot --platform managed
   ```

**Pros**: Scales to zero, pay-per-use
**Cons**: Requires Google Cloud account

---

## Database Setup for Production

### MongoDB Atlas (Recommended for Production)

1. **Create cluster**: Visit [mongodb.com/atlas](https://mongodb.com/atlas)
2. **Create database**: Name it `tax_data`
3. **Import your data**: Use MongoDB Compass or mongoimport
4. **Get connection string**: Replace `MONGO_URI` in your environment variables

### Example Connection String:
```
mongodb+srv://username:password@cluster.mongodb.net/tax_data?retryWrites=true&w=majority
```

---

## Performance Tips

### 1. Model Selection for Production
```python
# In model_config.py
CURRENT_MODEL_TIER = "balanced"  # Good speed/quality balance
FAST_MODE = True                 # Enable for production
```

### 2. Memory Optimization
- Use `google/flan-t5-base` instead of `flan-t5-large` for better speed
- Enable caching in production
- Use multiple workers: `gunicorn --workers 2 --threads 4`

### 3. Monitoring
- Check `/healthz` endpoint for health monitoring
- Monitor response times in logs
- Set up alerts for errors

---

## Troubleshooting

### Common Issues:

1. **Out of Memory**: Use smaller model (`flan-t5-small`)
2. **Slow Responses**: Enable `FAST_MODE=true`
3. **Database Connection**: Check `MONGO_URI` format
4. **Missing Embeddings**: Run `python ingest.py` first

### Debug Mode:
```bash
# Run with debug info
FLASK_ENV=development python app.py
```

---

## Security Checklist

- [ ] Use environment variables for secrets
- [ ] Enable HTTPS (automatic on Render/Railway)
- [ ] Set up database authentication
- [ ] Limit CORS if needed
- [ ] Monitor for unusual traffic

---

## Cost Estimates

| Platform | Free Tier | Paid Plans |
|----------|-----------|------------|
| Render | ✅ 500 hours/month | $7/month |
| Railway | ✅ $5 credit/month | $0.02/hour |
| Cloud Run | ✅ 2M requests/month | Pay-per-use |
| MongoDB Atlas | ✅ 512MB | $9/month |

---

## Support

If you encounter issues:
1. Check the logs first
2. Verify environment variables
3. Test locally before deploying
4. Check the health endpoint: `https://your-app.com/healthz`

Happy deploying! 🎉
