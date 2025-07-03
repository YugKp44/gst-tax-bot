# 🧾 How to Run the GST & Income Tax Chatbot Locally (Flask)
This guide walks you through running the chatbot on your local machine using Python and Flask.

---
### ✅ Prerequisites
Before starting, make sure you have:

- Python 3.10+
- `pip` (Python package manager)
- A terminal or command prompt (like Command Prompt, PowerShell, or Terminal)

---
### 📦 Step-by-Step Setup

**1. Clone the Project**
If you haven’t already, open your terminal and run:
```bash
git clone [https://github.com/YugKp44/gst-tax-bot.git](https://github.com/YugKp44/gst-tax-bot.git)
cd gst-tax-bot
```

**2. Create and Activate a Virtual Environment**
This keeps your project dependencies isolated.

*For Windows:*
```bash
python -m venv venv
venv\Scripts\activate
```

*For macOS/Linux:*
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**4. Download Required Models (First-time only)**
Run this snippet to download and cache the machine learning models locally. This might take a few minutes depending on your internet connection.
```bash
python -c "from sentence_transformers import SentenceTransformer; from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; print('Downloading embedding model...'); SentenceTransformer('all-MiniLM-L6-v2'); print('Downloading generation model...'); AutoTokenizer.from_pretrained('google/flan-t5-small'); AutoModelForSeq2SeqLM.from_pretrained('google/flan-t5-small'); print('All models downloaded.')"
```

**5. Run the Flask App**
The simplest way to run the application is by executing the `app.py` script directly.
```bash
python app.py
```
Alternatively, you can use the `flask` command.
```bash
# On Windows
set FLASK_APP=app.py

# On macOS/Linux
export FLASK_APP=app.py

# Now run the app
flask run
```

**6. Open in Browser**
Go to the following address in your web browser:
```
[http://127.0.0.1:5000](http://127.0.0.1:5000)
```
You should see the chatbot UI. Ask your questions and see responses based on GST & Income Tax law!

---
### 🛠️ Notes
- All model and retrieval logic is handled server-side via Flask.
- No internet connection is needed after the models are downloaded (assuming the FAISS index and metadata are local).
- To stop the app, press `Ctrl+C` in the terminal. To restart it after edits, just run `python app.py` or `flask run` again.
