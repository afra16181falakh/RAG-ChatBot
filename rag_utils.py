import chromadb
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Initialize embedding model and ChromaDB
model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("pdf_chunks")

def chunk_text(text, chunk_size=500):
    # Simple chunking by words
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def embed_and_store(chunks):
    embeddings = model.encode(chunks).tolist()
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        collection.add(
            documents=[chunk],
            embeddings=[emb],
            ids=[str(i)]
        )

def retrieve_relevant_chunks(query, top_k=3):
    query_emb = model.encode([query]).tolist()[0]
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k
    )
    return results['documents'][0]

import logging
import concurrent.futures
import threading

def answer_question(question, context):
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    prompt = f"Answer the question based on the context below in the simplest way possible.\n\nContext: {context}\n\nQuestion: {question}\nAnswer:"

    def generate():
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logging.error(f"Error generating content from Gemini API: {e}")
            return "Sorry, I am having trouble answering right now."

    # Use a thread with timeout to avoid indefinite blocking
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(generate)
        try:
            answer = future.result(timeout=15)  # 15 seconds timeout
        except concurrent.futures.TimeoutError:
            logging.error("Gemini API call timed out.")
            answer = "Sorry, the response took too long. Please try again later."

    return answer
