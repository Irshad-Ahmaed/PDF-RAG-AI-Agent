# 📄 PDF RAG AI Agent

A production-grade **Retrieval-Augmented Generation (RAG)** system designed to ingest, index, and query PDF documents using Google Gemini, Qdrant, and Inngest.

---

## 🌟 Overview

The **PDF RAG AI Agent** allows you to turn any PDF into a searchable knowledge base. It uses state-of-the-art embeddings to understand the semantic meaning of your documents and leverages Large Language Models (LLMs) to provide accurate, grounded answers to your questions.

## 🚀 What It Does

- **Intelligent PDF Ingestion**: Automatically parses and chunks PDF files into manageable, sentence-aware segments.
- **Semantic Search**: Uses Google Gemini embeddings to find the most relevant context for any given question.
- **AI-Powered Answers**: Generates natural language responses grounded strictly in the provided context, reducing hallucinations.
- **Reliable Workflows**: Powered by Inngest, ensuring that document processing and queries are handled as resilient, retriable background jobs.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Workflow Orchestration**: [Inngest](https://www.inngest.com/)
- **AI Models**: [Google Gemini](https://ai.google.dev/) (`gemini-2.0-flash-lite`, `gemini-embedding-2`)
- **Vector Database**: [Qdrant](https://qdrant.tech/)
- **Data Parsing**: [LlamaIndex](https://www.llamaindex.ai/)
- **Validation**: [Pydantic](https://docs.pydantic.dev/)

---

## 🧠 How It Works

1.  **Ingestion**: A PDF is uploaded/pointed to. It's split into chunks with 200-character overlaps to maintain context.
2.  **Embedding**: Each chunk is converted into a 768-dimensional vector using Google's embedding model.
3.  **Storage**: Vectors and metadata (the original text) are stored in Qdrant.
4.  **Query**: When a question is asked, it is also embedded.
5.  **Retrieval**: Qdrant finds the Top-K chunks most similar to the question vector.
6.  **Generation**: The chunks + the question are sent to Gemini to generate a factual answer.

---

## 💻 Local Setup & Installation

### 1. Prerequisites
- **Python**: 3.12+ (Recommended 3.13)
- **Docker**: For running Qdrant (recommended) or a local Qdrant instance.
- **Gemini API Key**: Obtain one from [Google AI Studio](https://aistudio.google.com/).

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/pdfs-rag-ai-agent.git
cd pdfs-rag-ai-agent
```

### 3. Setup Virtual Environment
```bash
# Create venv
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Mac/Linux)
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -e .
```
*Note: We recommend using [uv](https://github.com/astral-sh/uv) for faster installation: `uv sync`.*

### 5. Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_api_key_here
QDRANT_URL=http://localhost:6333
MODEL=gemini-2.0-flash-lite
```

### 6. Run Qdrant
If you have Docker:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

---

## 🏃 Running the Application

### 1. Start the Inngest Dev Server
Inngest requires a dev server to orchestrate events locally:
```bash
npx inngest-cli@latest dev
```

### 2. Start the FastAPI App
In a new terminal:
```bash
uvicorn main:app --reload --port 8000
```

### 3. Process a PDF
Send an event to Inngest (via the dashboard at `http://localhost:8288` or API) with the event `rag/inngest_pdf`:
```json
{
  "name": "rag/inngest_pdf",
  "data": {
    "pdf_path": "path/to/your/document.pdf",
    "source_id": "my-document-01"
  }
}
```

### 4. Ask a Question
Send an event with `rag/query_pdf_ai`:
```json
{
  "name": "rag/query_pdf_ai",
  "data": {
    "question": "What is the main topic of the document?",
    "top_k": 5
  }
}
```

---

## 📂 Project Structure
- `main.py`: Entry point and Inngest function definitions.
- `data_loader.py`: PDF processing and embedding logic.
- `vector_db.py`: Qdrant integration.
- `custom_types.py`: Pydantic data models.
- `diagrams/`: System architecture visualizations.
- `PROJECT_DOCUMENTATION.md`: Deep dive into the technical implementation.
