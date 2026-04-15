# What context Hub is About ?

This project is a simple Retrieval-Augmented Generation (RAG) application.

## Features
- Upload PDF
- Extract text
- Generate embeddings (Nomic)
- Store in Pinecone
- Ask questions
- Get answers using Groq LLM

## Tech Stack
- FastAPI (Backend)
- HTML, CSS, JS (Frontend)
- Pinecone (Vector DB)
- Nomic (Embeddings)
- Groq (LLM)

## Setup

### 1. Clone repo
git clone <your-repo-link>
cd rag-project

### 2. Install dependencies
pip install -r requirements.txt

### 3. Add .env file
Add your API keys:
GROQ_API_KEY=
PINECONE_API_KEY=
PINECONE_ENV=

### 4. Run backend
uvicorn main:app --reload

### 5. Open frontend
Open index.html in browser

## API Endpoints

POST /upload → Upload PDF  
POST /query → Ask question  

## Future Improvements
- Chat UI
- Streaming responses
- Better chunking
- Multi-PDF support