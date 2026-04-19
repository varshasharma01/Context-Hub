from fastapi import FastAPI, UploadFile, File, Query
from  google import genai
from fastapi.middleware.cors import CORSMiddleware
import nomic
import fitz  # PyMuPDF
from nomic import embed
# from groq import Groq

from pinecone import Pinecone
import os
from dotenv import load_dotenv
import string
from nomic import embed
import uuid

# Load env variablesz
load_dotenv()

from google import genai # Naya import

# Client initialize karein
client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")

NOMIC_API_KEY = os.getenv("NOMIC_API_KEY")
# Login to Nomic
if NOMIC_API_KEY:
    nomic.login(NOMIC_API_KEY)
else:
    print("Warning: NOMIC_API_KEY not found!")

# Init clients
# client = Groq(api_key=GROQ_API_KEY)

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("context-hub")

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


# 1. Update create_embeddings
def create_embeddings(chunks):
    if not chunks:
        return []
    response = embed.text(
        texts=chunks,
        model="nomic-embed-text-v1",
        task_type="search_document"
    )
    # Check if 'embeddings' key exists and is not empty
    if 'embeddings' in response and len(response['embeddings']) > 0:
        return response['embeddings']
    else:
        print("DEBUG: Nomic returned no embeddings!")
        return []
    
# 2. Update store_embeddings
def store_embeddings(chunks, embeddings):
    if not chunks or not embeddings:
        print("DEBUG: Nothing to store. Chunks or Embeddings are empty.")
        return

    vectors = []
    # Dono lists ki length same honi chahiye
    for i in range(len(embeddings)):
        unique_id = str(uuid.uuid4()) 
        vectors.append({
            "id": unique_id, 
            "values": embeddings[i], 
            "metadata": {"text": chunks[i]}
        })
    
    if vectors:
        index.upsert(vectors=vectors)
# 3. Update search
def search(query):
    query_response = embed.text(
        texts=[query],
        model="nomic-embed-text-v1",
        task_type="search_query"
    )
    query_emb = query_response['embeddings'][0]

    results = index.query(
        vector=query_emb,
        top_k=3,
        include_metadata=True
    )
    
    # Extract text safely
    relevant_chunks = []
    for match in results['matches']:
        if match.get('metadata') and 'text' in match['metadata']:
            relevant_chunks.append(match['metadata']['text'])
    
    return relevant_chunks


def generate_answer(query,context):
    # print(f"DEBUG: Context sent to Groq: {context[:200]}...") # Pehle 200 characters dekhein
    # if not context.strip():
    #     return "I'm sorry, I couldn't find any relevant text in the PDF to answer this."
    
    # response = client.chat.completions.create(
    #     model="llama3-70b-8192",
    #     messages=[
    #         {"role": "system", "content": "Answer only from given context"},
    #         {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
    #     ]
    # )
    # return response.choices[0].message.content
   
    
   
    try:
        prompt = f"Context: {context}\n\nQuestion: {query}"
        
        # 'gemini-1.5-flash' ki jagah 'models/gemini-1.5-flash' try karein
        # Aur safety ke liye hum system_instruction ko content se pehle define karte hain
        response = client_gemini.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=prompt,
            config={
                "system_instruction": "You are a helpful assistant. Answer ONLY using the provided context. If the answer is not there, say you don't know.\
                    and when you get answer elaborate and generate more information about the answer."
            }
        )
        
        # Gemini response object se text nikalne ka tarika
        if response and response.text:
            return response.text
        else:
            return "Gemini could not generate a response. Please check the context."

    except Exception as e:
        print(f"DEBUG Gemini Error: {str(e)}")
        return f"Gemini Error: {str(e)}"

# -------- ROUTES -------- #

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # STEP 1: Purana data delete karne ki koshish (with Try-Except)
        try:
            # delete_all=True kabhi kabhi error deta hai agar index empty ho
            index.delete(delete_all=True)
            print("DEBUG: Pinecone Index Cleared.")
        except Exception as e:
            
            print(f"DEBUG: Delete skipped or Index already empty: {e}")

        # STEP 2: Nayi file read aur process karo
        content = await file.read()
        pdf = fitz.open(stream=content, filetype="pdf")

        text = ""
        for page in pdf:
            text += page.get_text()

        if not text.strip():
            return {"error": "PDF is empty or could not be read."}

        # Chunks aur Embeddings
        chunks = chunk_text(text)
        embeddings = create_embeddings(chunks)
        store_embeddings(chunks, embeddings)

        return {"message": "New PDF processed successfully, old data cleared."}
    
    except Exception as e:
        print(f"Upload Error: {e}")
        return {"error": f"Internal Server Error: {str(e)}"}
    
@app.post("/query")
async def query_pdf(query: str = Query(...)): # Explicitly define as a query param
    # results = search(query)
    # context = " ".join(results)
    
    # # Temporarily just return the context to see if Pinecone is working
    # return {"answer": f"Found Context: {context}"}
    
    try:
        results = search(query)
        if not results:
            return {"answer": "I couldn't find any relevant information in the document."}
            
        context = " ".join(results)
        
        answer = generate_answer(query, context)

        return {"answer": answer, "context": context}
        # answer = generate_answer(query)
        # return {"answer": answer}
    
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}