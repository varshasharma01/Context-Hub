# 🚀 Context Hub – Multi-Modal RAG Application

Context Hub is a multi-modal AI application that allows users to interact with PDFs, Images, URLs, and YouTube videos using Retrieval-Augmented Generation (RAG) and modern LLMs.

---

## 🔥 Features

### 📄 PDF Intelligence
- Upload PDF documents
- Extract text and create embeddings
- Store embeddings in Pinecone
- Ask context-based questions

### 🖼️ Image Intelligence
- Upload images
- Ask questions about image content
- Uses Gemini Vision for understanding

### 🌐 URL Intelligence
- Paste any website URL
- Extract content using web scraping
- Ask questions or get summaries

### 🎥 YouTube Intelligence
- Extract transcripts from videos
- Convert transcripts into embeddings
- Ask questions based on video content

---

## 🧠 Architecture

### PDF & YouTube (RAG Pipeline)
Input → Text Extraction → Chunking → Embeddings (Nomic) → Pinecone → Retrieval → Gemini → Answer

### Image (Vision Pipeline)
Image → Gemini Vision → Answer

### URL (Web Pipeline)
URL → Scraping → Gemini → Answer

---

## 🛠️ Tech Stack

- Frontend: Streamlit
- Backend: FastAPI
- LLM: Gemini (Google GenAI)
- Embeddings: Nomic Embed
- Vector Database: Pinecone
- PDF Processing: PyMuPDF
- Web Scraping: BeautifulSoup
- YouTube: youtube-transcript-api

---

## 📁 Project Structure

context-hub/
│── backend/
│   │── main.py
│   │── .env
│
│── frontend/
│   │── app.py
│
│── requirements.txt
│── README.md
│── .gitignore

---

## ⚙️ Setup Instructions

### 1. Clone Repository
git clone https://github.com/varshasharma01/Context-Hub.git  
cd context-hub  

---

### 2. Install Dependencies
pip install -r requirements.txt  

---

### 3. Create .env File

GEMINI_API_KEY=your_gemini_key  
PINECONE_API_KEY=your_pinecone_key  
NOMIC_API_KEY=your_nomic_key  

---

### 4. Run Backend
uvicorn backend.main:app --reload  

---

### 5. Run Frontend
streamlit run frontend/app.py  

---

## 🔗 API Endpoints

POST /upload → Upload PDF  
POST /query → Query PDF  

POST /process-image → Upload Image  
POST /query-image → Query Image  

POST /process-url → Analyze URL  
POST /query-url → Query URL  

POST /process-youtube → Process YouTube  
POST /query-youtube → Query YouTube  

---

## ⚡ Key Highlights

- Multi-modal AI system (PDF, Image, URL, YouTube)
- RAG-based architecture for accurate answers
- Fast embedding using Nomic
- Efficient retrieval using Pinecone
- Clean UI with Streamlit tabs
- Handles real-world edge cases

---

## 🚀 Future Improvements

- Chat history
- Multi-document support
- YouTube timestamp answers
- Streaming responses
- Deployment (Docker / Cloud)

---

## 👩‍💻 Author

Varsha

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!