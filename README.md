# 🤖 GST & Income Tax Chatbot (India)

A smart, searchable chatbot that answers real-world queries related to **Indian GST** and **Income Tax** laws — including GSTR filings, TDS, ITC, and more. Built using **Flask**, **FAISS**, and **transformers** for fast semantic search and generation.

---

## 📌 Features

- 🔍 Semantic search with **FAISS** + **SentenceTransformers**
- 🧠 Answer generation using **Flan-T5-small** model
- ⚡ Fast response time (~3–5 sec locally)
- 📄 Handles both factual and situational tax queries

- 📚 Real-world examples: B2B/B2C, TDS limits, 80C deductions, etc.

---

## 🧱 Tech Stack

| Component          | Tech Used                                 |
| :----------------- | :---------------------------------------- |
| **Framework**      | Flask (Python)                            |
| **Search Engine**  | FAISS + `all-MiniLM-L6-v2` embeddings     |
| **Language Model** | Google `flan-t5-small` (via Transformers) |
| **Deployment**     | Docker / Google Cloud                     |

---

## 📄 Documentation & Getting Started

For detailed information on how to run, build, and understand the project, please refer to the documents in the `docs/` directory.

| Document                                            | Description                                             |
| :-------------------------------------------------- | :------------------------------------------------------ |
| **[RUN_INSTRUCTIONS.md](documentation/RUN_INSTRUCTION.md)** | Step-by-step guide to run the chatbot locally.          |
| **[MODEL_BUILD.md](documentation/MODEL_BUILD.md)**           | Explanation of the RAG pipeline and model architecture. |
| **[DATA_SOURCES.md](documentation/DATA_SOURCE.md)**         | A complete list of all data sources used.               |


---

## 📁 Project Structure

```
gst-tax-bot/
│
├── app.py              # Main Flask app
├── model.py            # Loads Flan-T5 model for generation
├── retrieve.py         # FAISS-based semantic search
│
├── docs/               # All documentation files
│   ├── RUN_INSTRUCTIONS.md
│   ├── MODEL_BUILD.md
│   └── DATA_SOURCES.md
│
├── samples/
│   └── interaction_logs.md
│
├── templates/
│   └── index.html      # Chatbot UI
│
├── static/
│   ├── style.css       # Chat UI styling
│   └── chat.js         # JS for frontend interaction
│
├── requirements.txt    # Python dependencies
└── README.md           # You're reading it
```

---

## 🙋‍♂️ Author

- **Yug KP**
- **Email**: `yugkpatil44@gmail.com`
- **GitHub**: `YugKp44`
