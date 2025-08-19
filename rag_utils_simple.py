import chromadb
import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Initialize ChromaDB with persistent storage
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Create or get collection
try:
    collection = chroma_client.get_or_create_collection(
        name="pdf_chunks",
        metadata={"hnsw:space": "cosine"}
    )
except Exception as e:
    logging.error(f"Error initializing ChromaDB: {e}")
    collection = None

def chunk_text(text, chunk_size=1000, overlap=100):
    """Split text into chunks with overlap for better context preservation"""
    if not text:
        return []
    
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def embed_and_store(chunks):
    """Store document chunks with their embeddings using ChromaDB's built-in embeddings"""
    if not collection:
        raise Exception("ChromaDB collection not initialized")
    
    if not chunks:
        raise Exception("No text chunks to process")

    try:
        # Clear existing collection
        existing_ids = collection.get()['ids']
        if existing_ids:
            collection.delete(ids=existing_ids)
        
        # Use ChromaDB's built-in embedding function
        collection.add(
            documents=chunks,
            ids=[str(i) for i in range(len(chunks))]
        )
        
        logging.info(f"Successfully processed {len(chunks)} chunks")
    except Exception as e:
        logging.error(f"Error in embedding and storing: {e}")
        raise Exception(f"Failed to process document: {str(e)}")

def retrieve_relevant_chunks(query, top_k=3):
    """Retrieve most relevant chunks for the query"""
    if not collection:
        raise Exception("ChromaDB collection not initialized")

    try:
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        return results['documents'][0] if results['documents'] else []
    except Exception as e:
        logging.error(f"Error in retrieval: {e}")
        return []

def answer_question(question, context):
    """Generate response using Gemini model"""
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        # Check if it's a general conversation
        general_chat_keywords = ['hi', 'hello', 'hey', 'how are you', 'good morning', 'good afternoon', 'good evening', 'thanks', 'thank you']
        is_general_chat = any(keyword in question.lower() for keyword in general_chat_keywords)
        
        if is_general_chat:
            prompt = f"""You are a friendly and helpful AI assistant named PDF Chatbot. 
            Respond to this greeting in a friendly and engaging way: {question}
            Keep the response concise but warm and welcoming."""
        else:
            prompt = f"""You are a helpful AI assistant. Answer the question based on the provided context.
            Be friendly and conversational in your response. If the question isn't related to the 
            context, politely mention that you're here to help with the PDF content.

            Context: {context}

            Question: {question}
            Answer: """

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Error generating content from Gemini API: {e}")
        return "I apologize, but I'm having trouble responding right now. Please try again in a moment."
