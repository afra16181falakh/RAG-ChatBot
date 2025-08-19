# PDF RAG Chatbot

A powerful AI-powered chatbot that lets you upload PDF documents and ask questions about their content using Retrieval-Augmented Generation (RAG) technology.

##  Features

-  **PDF Upload & Processing** - Upload any PDF document and extract text automatically
-  **AI Chat Interface** - Ask questions about your PDF and get instant, intelligent answers
-  **RAG Technology** - Uses advanced retrieval-augmented generation for accurate responses
-  **User Authentication** - Secure login/signup system with SQLite database
-  **Modern UI** - Beautiful, responsive interface built with Streamlit
-  **Auto-clear Input** - Text box automatically clears after each question
-  **Chat History** - View your conversation history with the AI

##  Tech Stack

- **Frontend**: Streamlit (Python)
- **AI/ML**: Google Gemini API
- **Vector Database**: ChromaDB
- **Text Processing**: LangChain
- **Authentication**: SQLite with bcrypt
- **PDF Processing**: PyPDF2

##  Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/pdf-rag-chatbot.git
   cd pdf-rag-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

##  Requirements

All dependencies are listed in `requirements.txt`:
- streamlit
- google-generativeai
- chromadb
- langchain
- pypdf2
- python-dotenv
- bcrypt

##  Usage

1. **Sign Up/Login** - Create an account or login to access the chatbot
2. **Upload PDF** - Click "Browse files" to upload your PDF document
3. **Wait for Processing** - The system will extract and index your document
4. **Start Chatting** - Ask questions about your PDF in the chat interface
5. **Clear Chat** - Use the clear button to start fresh conversations


