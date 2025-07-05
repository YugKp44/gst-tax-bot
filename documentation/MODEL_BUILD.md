# 💬 Indian Tax Chatbot – GST & Income Tax FAQ Assistant

This project is a **semantic search + generative chatbot** built to assist users with **Indian GST and Income Tax** questions. It leverages a Retrieval-Augmented Generation (RAG) pipeline, using state-of-the-art transformer models for both **document retrieval** and **answer generation**. The application is containerized with Docker and can be easily deployed to cloud platforms like Google Cloud Run.

---

## 🔧 How It Works

The chatbot follows a two-stage process: first, it retrieves relevant information from a knowledge base, and second, it uses that information to generate a human-like answer.

### 1. Data Collection & Preparation

-   📄 **Source Documents**: The knowledge base was built using FAQs and official PDF documents from government portals such as [cbic-gst.gov.in](https://cbic-gst.gov.in) and [incometax.gov.in](https://incometax.gov.in), along with other reliable educational tax resources.
    -   *Examples*: `FAQsonTDS.pdf`, `GST_FAQs.pdf`, `AdvanceTax_FAQs.pdf`

-   🔁 **Parsing and Structuring**:
    -   The `pdfplumber` library was used to extract questions and answers from the source PDFs.
    -   This data was cleaned and structured into a standardized JSON format, which serves as the foundation for our knowledge base.
    -   **Output File**: `data/faqs.json`

    ```json
    {
      "question": "What is GSTR-3B?",
      "answer": "GSTR-3B is a monthly self-declaration filed by registered taxpayers...",
      "source": "cbic-gst.gov.in"
    }
    ```

### 2. Retrieval Model (Semantic Search)

-   🔍 **Embedding Model**: We use [`sentence-transformers/all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), a fast and lightweight model that generates 384-dimensional vector embeddings. It's highly optimized for CPU inference and ideal for high-speed similarity search.

-   🧠 **Vector Indexing**:
    -   **FAISS (Facebook AI Similarity Search)** is used to create a dense vector index of all the FAQ embeddings.
    -   When a user asks a question, this retrieval system finds the top-k (e.g., 3) most semantically relevant Q&A pairs from the index.

-   📁 **Saved Artifacts**:
    -   `embeddings/faiss.index`: The FAISS vector database.
    -   `embeddings/faq_meta.pkl`: A pickle file containing the metadata (original questions and answers) corresponding to the vectors.

### 3. Generative Model (Answer Generation)

-   🤖 **Generation Model**: The core of our answer generation is [`google/flan-t5-base`](https://huggingface.co/google/flan-t5-base). This is a lightweight and efficient text-to-text model that is instruction-tuned, making it perfect for question-answering tasks.

-   ✍️ **Prompt Engineering**: The model is prompted to act as a tax expert and use the retrieved context to formulate a concise answer.

    ```text
    You are an expert on Indian GST & Income‑Tax law. Use the following context to write a concise answer:

    Context:
    Q: What is GSTR-1?
    A: It is a monthly or quarterly return of outward supplies...

    Question:
    What is GSTR-1?

    Answer:
    ```

-   🧽 **Post-processing**: The generated output is cleaned to remove source tags, fix bullet points, and improve spacing for better readability.

### 4. Backend Application

-   **API**: A simple and robust backend is built using **Flask**.
    -   `/ask` (`POST`): The main endpoint that accepts a user's question and returns a generated answer.
    -   `/` (`GET`): Serves a basic frontend chat interface (optional).
    -   `/healthz` (`GET`): A health check endpoint for deployment readiness probes.

-   **Containerization**: The application is fully **Dockerized**.
    -   Uses a `python:3.10-slim` base image for a small footprint.
    -   Models are cached during the image build process to minimize cold start times on serverless platforms.

---

## 📦 Tech Stack

| Layer          | Tool/Model                          |
| -------------- | ----------------------------------- |
| **Retrieval**  | `sentence-transformers` + **FAISS** |
| **Generation** | `google/flan-t5-base`              |
| **Backend**    | **Flask** + **Gunicorn**            |
| **Packaging**  | **Docker**                          |
| **Deployment** | **Google Cloud**                    |

---

## 📁 Directory Structure

```bash
.
├── app.py              # Flask backend application
├── model.py            # Answer generation logic (Flan-T5)
├── retrieve.py         # Semantic search logic (FAISS)
├── ingest.py           # Script to build embeddings and FAISS index
├── data/
│   ├── faqs.json       # Structured Q&A data
│   └── raw/            # Source PDF documents
├── embeddings/
│   ├── faiss.index     # The saved FAISS index
│   └── faq_meta.pkl    # Metadata for the indexed FAQs
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🚀 Deployment

The application is designed for easy deployment. Build the Docker image and run it on your preferred cloud provider.

```bash
# 1. Build the Docker image
docker build -t indian-tax-chatbot .

# 2. Run the container locally
docker run -p 8080:8080 indian-tax-chatbot
```

The application will be available at `http://localhost:8080`.

---

## 🛠 Next Steps

-   **Model Optimization**: Replace `Flan-T5-base` with a faster, quantized LLM like **Phi-2** or **TinyLlama** to improve inference speed.
-   **Stateful Conversations**: Add session memory to handle follow-up questions and create a more conversational experience.
-   **Feedback Loop**: Implement a mechanism for users to provide feedback on answers, which can be used to fine-tune the model.
-   **Real-time Data**: Integrate with government APIs to fetch real-time tax information and updates.

---

## 👨‍💻 Maintainer

-   **Yug KP**
-   **Email**: `yugkpatil44@gmail.com`
-   **GitHub**: `YugKp44`
