# 🔍 ContextHub — Multimodal RAG Intelligence Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B?style=for-the-badge&logo=streamlit)
![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-black?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3-orange?style=for-the-badge)

> **Ask questions from your PDFs, Images, Websites, and YouTube Videos — grounded strictly in your data.**

</div>

---

## 📌 What is ContextHub?

ContextHub is a **Retrieval-Augmented Generation (RAG)** platform that lets you upload any source of information and query it using natural language.  
Unlike general-purpose AI, ContextHub answers **only from your uploaded content** — no hallucinations, no guesswork.

---

## ✨ Features

| Mode | Input | Model Used |
|------|-------|-----------|
| 📄 PDF Analysis | Upload any PDF | Groq — LLaMA 3.3 70B |
| 🖼️ Image Intelligence | JPG / PNG | Google Gemini Vision |
| 🔗 Web Intelligence | Any public URL | Groq — LLaMA 3.3 70B |
| 🎥 YouTube Intelligence | YouTube URL | Groq — LLaMA 3.3 70B |

- 🧠 **Nomic Embeddings** — semantic vector search
- 📦 **Pinecone** — isolated namespaces per source, no data bleed
- ⚡ **Groq** — ultra-fast LLM inference
- 👁️ **Gemini** — multimodal image understanding
- 🖥️ **Streamlit** — clean tabbed UI with session management

---

## 🧠 Architecture

### PDF & YouTube — RAG Pipeline
```
Input → Text Extraction → Chunking → Nomic Embeddings
     → Pinecone (isolated namespace) → Similarity Search
     → Top-K Chunks → Groq LLM → Answer
```

### Image — Vision Pipeline
```
Image Upload → Base64 Encode → Gemini Vision API → Answer
```

### URL — Web Pipeline
```
URL → BeautifulSoup Scraping → Groq LLM → Answer
```

---

## 📁 Project Structure

```
context-hub/
│
├── backend/
│   ├── main.py              # FastAPI server — all routes & RAG logic
│   └── .env                 # API keys (never commit this)
│
├── frontend/
│   └── app.py               # Streamlit UI — tabs, session state, previews
│
├── requirements.txt         # All Python dependencies
├── run.sh                   # One-command startup script
├── .gitignore
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/varshasharma01/Context-Hub.git
cd context-hub
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file inside the `backend/` folder:

```env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
NOMIC_API_KEY=your_nomic_api_key
```

> **Get your keys from:**
> - Groq → https://console.groq.com
> - Gemini → https://aistudio.google.com
> - Pinecone → https://app.pinecone.io
> - Nomic → https://atlas.nomic.ai

### 4. Run the Project (One Command)

```bash
chmod +x run.sh    # first time only
./run.sh
```

This starts both servers together:
- ⚙️ FastAPI backend → `http://localhost:8000`
- 🖥️ Streamlit frontend → `http://localhost:8501`

> **Or run manually in two terminals:**
> ```bash
> # Terminal 1
> uvicorn backend.main:app --reload
>
> # Terminal 2
> streamlit run frontend/app.py
> ```

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload & index a PDF |
| `POST` | `/query` | Query the indexed PDF |
| `POST` | `/process-image` | Upload & store an image |
| `POST` | `/query-image` | Query the image via Gemini |
| `POST` | `/process-url` | Scrape & store a webpage |
| `POST` | `/query-url` | Query the webpage content |
| `POST` | `/process-youtube` | Fetch & index YouTube transcript |
| `POST` | `/query-youtube` | Query the video transcript |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | FastAPI |
| LLM (Text) | Groq — LLaMA 3.3 70B Versatile |
| LLM (Vision) | Google Gemini |
| Embeddings | Nomic Embed Text v1 / Vision v1.5 |
| Vector Database | Pinecone |
| PDF Parsing | PyMuPDF (fitz) |
| Web Scraping | BeautifulSoup4 |
| Transcripts | youtube-transcript-api |

---

## ⚡ Key Highlights

- **True multimodal RAG** — 4 input types in one platform
- **Namespace isolation** — each source gets its own Pinecone namespace, zero data bleed between uploads
- **Session-aware UI** — answers clear on new uploads, no stale responses
- **Dual AI providers** — Groq for speed, Gemini for vision
- **One-command startup** — `run.sh` boots both servers together

---

## 🚀 Future Improvements

- [ ] Chat history with memory
- [ ] Multi-document support (query across multiple PDFs)
- [ ] YouTube timestamp-based answers
- [ ] Streaming responses
- [ ] Docker containerization
- [ ] Cloud deployment (Render + Streamlit Cloud)

---

## 👩‍💻 Author

**Varsha Sharma**  

[![GitHub](https://img.shields.io/badge/GitHub-varshasharma01-black?style=flat&logo=github)](https://github.com/varshasharma01)

---

## ⭐ Support

If you found this useful, consider giving it a ⭐ on GitHub !