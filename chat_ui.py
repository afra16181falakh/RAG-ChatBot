import streamlit as st
from pdf_utils import extract_text_from_pdf
from rag_utils import chunk_text, embed_and_store, retrieve_relevant_chunks, answer_question

# --- Custom CSS for Gen Z animated UI ---
st.markdown("""
     <style>
    .header {
        font-size: 3em;
        font-weight: 800;
        background: linear-gradient(90deg, #00B4DB, #0083B0, #6dd5ed);
        background-size: 200% 200%;
        color: transparent;
        -webkit-background-clip: text;
        background-clip: text;
        animation: gradientMove 8s ease infinite;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .chat-bubble {
        padding: 1.2em 1.4em;
        border-radius: 1.5em;
        margin-bottom: 1.2em;
        max-width: 85%;
        font-size: 1.1em;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .user-bubble {
        background: linear-gradient(135deg, #6dd5ed 0%, #2193b0 100%);
        color: white;
    }
    .bot-bubble {
        background: linear-gradient(135deg, #141E30 0%, #243B55 100%);
        color: white;
    }
    .pdf-status {
        background: rgba(255,255,255,0.1);
        padding: 1em;
        border-radius: 1em;
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(5px);
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar for branding and instructions ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/337/337946.png", width=80)
    st.markdown("## PDF RAG Chatbot")
    st.markdown("Upload a PDF and chat with it using AI. Ask anything about your document and get clear, simple answers.")
    st.markdown("---")
    uploaded_file = st.file_uploader("Upload your PDF", type="pdf")
    st.markdown("---")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
    
    st.info("Powered by Python, LangChain, ChromaDB, and Gemini.")

# --- Main header ---
st.markdown('<div class="header">🤖 PDF Chatbot </div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Ask questions about your PDF and get instant, AI-powered answers.</div>', unsafe_allow_html=True)

# --- Session state for chat history and PDF processing ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pdf_processed" not in st.session_state:
    st.session_state.pdf_processed = False
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""

# --- PDF Processing ---
if uploaded_file and not st.session_state.pdf_processed:
    with st.spinner("✨ Extracting and indexing your PDF..."):
        text = extract_text_from_pdf(uploaded_file)
        chunks = chunk_text(text)
        embed_and_store(chunks)
        st.session_state.pdf_processed = True
        st.session_state.pdf_name = uploaded_file.name
        st.success("PDF processed! Start chatting below.")

# --- Show PDF status ---
if st.session_state.pdf_processed:
    st.markdown(f'<div class="pdf-status">📄 <b>Loaded:</b> {st.session_state.pdf_name}</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="pdf-status">📄 <b>No PDF loaded.</b> Please upload a PDF to begin.</div>', unsafe_allow_html=True)

# --- Chat Interface ---
if st.session_state.pdf_processed:
    # Use a form to handle input submission and clearing
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Type your question and press Enter", 
            key="question_input",
            placeholder="Ask anything about your PDF..."
        )
        submitted = st.form_submit_button("Send", use_container_width=True)
        
        if submitted and user_input:
            with st.spinner("🤖 Thinking..."):
                try:
                    context = " ".join(retrieve_relevant_chunks(user_input))
                    answer = answer_question(user_input, context)
                except Exception as e:
                    answer = "Sorry, something went wrong while processing your question."
                    st.error(f"Error: {e}")
                
                st.session_state.chat_history.append(("user", user_input))
                st.session_state.chat_history.append(("bot", answer))
                st.rerun()

    # --- Display chat history as animated chat bubbles ---
    # This should be outside the if user_input block!
    # So it always shows the chat history
    for idx, (sender, message) in enumerate(st.session_state.chat_history):
        st.markdown(
            f"""
            <div class="chat-bubble {'user-bubble' if sender == 'user' else 'bot-bubble'}" style="animation-delay: {0.1*idx}s;">
                {message}
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.info("Please upload a PDF to get started.")

# --- Footer ---
st.markdown('<div class="footer">Made with 💜 by <b>Afra Falakh</b> &middot; AIML Engineer </div>', unsafe_allow_html=True)