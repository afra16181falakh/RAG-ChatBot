import streamlit as st
from pdf_utils import extract_text_from_pdf
from rag_utils import chunk_text, embed_and_store, retrieve_relevant_chunks, answer_question

# --- Custom CSS for Gen Z animated UI ---
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #f7fafd 0%, #e0c3fc 100%);
    }
    .header {
        font-size: 2.7em;
        font-weight: bold;
        background: linear-gradient(90deg, #6dd5ed, #2193b0, #e0c3fc, #f7971e);
        background-size: 400% 400%;
        color: transparent;
        -webkit-background-clip: text;
        background-clip: text;
        animation: gradientMove 6s ease-in-out infinite;
        margin-bottom: 0.1em;
        letter-spacing: 1px;
        text-align: center;
    }
    @keyframes gradientMove {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .subheader {
        font-size: 1.2em;
        color: #555;
        margin-bottom: 1.5em;
        text-align: center;
        animation: fadeIn 2s;
    }
    .chat-bubble {
        padding: 1em 1.2em;
        border-radius: 1.2em;
        margin-bottom: 1em;
        max-width: 70%;
        font-size: 1.1em;
        box-shadow: 0 2px 12px rgba(44,62,80,0.13);
        line-height: 1.5;
        opacity: 0;
        animation: fadeInUp 0.7s forwards;
        transition: transform 0.2s;
    }
    .chat-bubble:hover {
        transform: scale(1.03) translateY(-2px);
        box-shadow: 0 4px 18px rgba(44,62,80,0.18);
    }
    .user-bubble {
        background: linear-gradient(90deg, #f7971e 0%, #ffd200 100%);
        color: #222;
        margin-left: auto;
        text-align: right;
        border-bottom-right-radius: 0.3em;
        border-top-right-radius: 1.5em;
    }
    .bot-bubble {
        background: linear-gradient(90deg, #6dd5ed 0%, #2193b0 100%);
        color: white;
        margin-right: auto;
        text-align: left;
        border-bottom-left-radius: 0.3em;
        border-top-left-radius: 1.5em;
    }
    .pdf-status {
        font-size: 1em;
        color: #2193b0;
        margin-bottom: 1em;
        text-align: center;
        animation: fadeIn 1.5s;
    }
    .footer {
        font-size: 0.95em;
        color: #888;
        margin-top: 2em;
        text-align: center;
        animation: fadeIn 2s;
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px);}
        to { opacity: 1; transform: translateY(0);}
    }
    @keyframes fadeIn {
        from { opacity: 0;}
        to { opacity: 1;}
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
    st.info("Powered by Python, LangChain, ChromaDB, and Gemini.")

# --- Main header ---
st.markdown('<div class="header">🤖 PDF Chatbot Demo</div>', unsafe_allow_html=True)
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
    user_input = st.text_input("Type your question and press Enter", key="input", placeholder="Ask anything about your PDF...")

    if user_input:
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
    for idx, (sender, message) in enumerate(st.session_state.chat_history):
        # Add a slight delay to each bubble for a "pop-in" effect
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
st.markdown('<div class="footer">Made with 💜 by <b>Afra Falakh</b> &middot; AIML Engineer Demo</div>', unsafe_allow_html=True)