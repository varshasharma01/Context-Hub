from fastapi import FastAPI, UploadFile, File, Query
from  google import genai
from fastapi.middleware.cors import CORSMiddleware
import nomic
# for pdf
import fitz  # PyMuPDF
from nomic import embed
from pinecone import Pinecone
import os
from dotenv import load_dotenv
import string
from nomic import embed
import uuid
# for URL
import requests
from bs4 import BeautifulSoup
# for image
import base64
import io
from PIL import Image
# for youtube video 

from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
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
            index.delete(delete_all=True, namespace="")
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

        # return {"answer": answer, "context": context}
        # answer = generate_answer(query)
        return {"answer": answer}
    
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}
    
def create_image_embedding(image):
    output = embed.image(
        images=[image],
        model="nomic-embed-vision-v1.5"
    )
    return output["embeddings"][0]

def store_image_embedding(image_vector, filename):
    index.upsert([
        {
            "id": str(uuid.uuid4()),
            "values": image_vector,
            "metadata": {
                "type": "image",
                "filename": filename
            }
        }
    ])
    
    
IMAGE_NAMESPACE = "image"

def store_image_embedding(image_vector, filename):
    index.upsert(
        vectors=[{
            "id": str(uuid.uuid4()),
            "values": image_vector,
            "metadata": {
                "type": "image",
                "filename": filename
            }
        }],
        namespace=IMAGE_NAMESPACE
    )


def generate_image_answer(query, image):
    try:
        # Convert image → bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_bytes = img_byte_arr.getvalue()

        # Convert to base64
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")

        response = client_gemini.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {"text": query},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": img_base64
                            }
                        }
                    ]
                }
            ]
        )

        return response.text if response.text else "No answer generated."

    except Exception as e:
        return f"Error: {str(e)}"
    

current_image = None

@app.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    global current_image

    try:
        image = Image.open(file.file)
        current_image = image  #  store for query

        # optional embedding
        image_vector = create_image_embedding(image)
        store_image_embedding(image_vector, file.filename)

        return {"message": "Image processed successfully"}

    except Exception as e:
        return {"error": str(e)}

@app.post("/query-image")
async def query_image(query: str = Query(...)):
    global current_image

    try:
        if current_image is None:
            return {"error": "No image uploaded"}

        answer = generate_image_answer(query, current_image)

        return {"answer": answer}

    except Exception as e:
        return {"error": str(e)}
 
##########################################################################################################    
    
def extract_text_from_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # remove scripts/styles
        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text(separator=" ")

        return text[:5000]   # limit (VERY IMPORTANT)

    except Exception as e:
        print("URL Error:", e)
        return None
    
def generate_url_answer(url, query=None):
    text = extract_text_from_url(url)

    if not text:
        return "Could not fetch content from this URL."

    try:
        prompt = f"""
        You are given content from a webpage.

        URL: {url}

        Content:
        {text}

        Task:
        Explain what this page is about in simple words.
        """

        if query:
            prompt += f"\n\nUser Question: {query}"

        response = client_gemini.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        return response.text if response.text else "No response."

    except Exception as e:
        return f"Error: {str(e)}"
    
    
current_url = None
current_url_text = None


@app.post("/process-url")
async def process_url(url: str = Query(...)):
    global current_url, current_url_text

    text = extract_text_from_url(url)

    if not text:
        return {"error": "Failed to extract content"}

    current_url = url
    current_url_text = text

    return {"message": "URL processed successfully"}


@app.post("/query-url")
async def query_url(query: str = Query(...)):
    global current_url, current_url_text

    if not current_url_text:
        return {"error": "No URL processed"}

    try:
        prompt = f"""
        URL: {current_url}

        Content:
        {current_url_text}

        Question: {query}
        """

        response = client_gemini.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        return {"answer": response.text}

    except Exception as e:
        return {"error": str(e)}
    
    
##########################################################################################################



def get_video_id(url):
    parsed_url = urlparse(url)

    if "youtube.com" in url:
        return parse_qs(parsed_url.query).get("v", [None])[0]
    elif "youtu.be" in url:
        return parsed_url.path.strip("/")
    
    return None

def get_transcript(url):
    try:
        video_id = get_video_id(url)
        if not video_id:
            return "ERROR: Invalid YouTube URL"

        ytt_api = YouTubeTranscriptApi()  # instantiate in new version

        # Try fetching English first, then any available language
        try:
            transcript_data = ytt_api.fetch(video_id, languages=['en'])
        except NoTranscriptFound:
            # Get list of available transcripts and pick first
            transcript_list = ytt_api.list(video_id)
            available = list(transcript_list)
            if not available:
                return "ERROR: No transcripts available for this video"
            transcript_data = available[0].fetch()

        # New API returns objects with .text attribute
        text = " ".join([t.text for t in transcript_data])
        return text

    except TranscriptsDisabled:
        return "ERROR: Transcripts are disabled for this video"
    except Exception as e:
        return f"ERROR: {str(e)}"
    
YOUTUBE_NAMESPACE = "youtube"
@app.post("/process-youtube")
async def process_youtube(url: str = Query(...)):
    try:
        try:
            index.delete(delete_all=True, namespace=YOUTUBE_NAMESPACE)
        except Exception as e:
            print(f"DEBUG: YouTube namespace clear skipped: {e}")

        text = get_transcript(url)

        if text.startswith("ERROR"):
            return {"error": text}

        chunks = chunk_text(text, size=1000)
        embeddings = create_embeddings(chunks)

        if not embeddings:
            return {"error": "Failed to create embeddings"}

        vectors = [
            {
                "id": str(uuid.uuid4()),
                "values": embeddings[i],
                "metadata": {"text": chunks[i]}
            }
            for i in range(len(embeddings))
        ]

        index.upsert(vectors=vectors, namespace=YOUTUBE_NAMESPACE)
        return {"message": f"YouTube video processed successfully ({len(chunks)} chunks)"}

    except Exception as e:
        return {"error": str(e)}
    

@app.post("/query-youtube")
async def query_youtube(query: str = Query(...)):
    try:
        query_emb = embed.text(
            texts=[query],
            model="nomic-embed-text-v1",
            task_type="search_query"
        )["embeddings"][0]

        results = index.query(
            vector=query_emb,
            top_k=5,
            include_metadata=True,
            namespace=YOUTUBE_NAMESPACE
        )

        context = "\n\n".join([
            match["metadata"]["text"]
            for match in results["matches"]
        ])

        answer = generate_answer(query, context)

        return {"answer": answer}

    except Exception as e:
        return {"error": str(e)}