from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
from nomic import embed
from groq import Groq
import pinecone
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")

# Init clients
client = Groq(api_key=GROQ_API_KEY)

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
index = pinecone.Index("rag-index")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- HELPER FUNCTIONS -------- #

def chunk_text(text, size=500):
    return [text[i:i+size] for i in range(0, len(text), size)]


def create_embeddings(chunks):
    embeddings = []
    for chunk in chunks:
        emb = embed.text(
            texts=[chunk],
            model="nomic-embed-text-v1"
        )[0]
        embeddings.append(emb)
    return embeddings


def store_embeddings(chunks, embeddings):
    vectors = []
    for i, emb in enumerate(embeddings):
        vectors.append((
            f"id_{i}",
            emb,
            {"text": chunks[i]}
        ))
    index.upsert(vectors)


def search(query):
    query_emb = embed.text(
        texts=[query],
        model="nomic-embed-text-v1"
    )[0]

    results = index.query(
        vector=query_emb,
        top_k=3,
        include_metadata=True
    )

    return [match["metadata"]["text"] for match in results["matches"]]


def generate_answer(query, context):
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "Answer only from given context"},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ]
    )
    return response.choices[0].message.content


# -------- ROUTES -------- #

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    content = await file.read()

    pdf = fitz.open(stream=content, filetype="pdf")

    text = ""
    for page in pdf:
        text += page.get_text()

    chunks = chunk_text(text)
    embeddings = create_embeddings(chunks)
    store_embeddings(chunks, embeddings)

    return {"message": "PDF processed successfully"}


@app.post("/query")
async def query_pdf(query: str):
    results = search(query)
    context = " ".join(results)

    answer = generate_answer(query, context)

    return {"answer": answer}