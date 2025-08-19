import streamlit as st
from pdf_utils import extract_text_from_pdf
from rag_utils_simple import chunk_text, embed_and_store, retrieve_relevant_chunks, answer_question
from auth import login_user, signup_user, logout

# Page configuration
st.set_page_config(
    page_title="PDF RAG Chatbot", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'

def login_page():
    st.title("🔐 Login to PDF Chatbot")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", type="primary"):
            if login_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    with tab2:
        st.subheader("Sign Up")
        new_username = st.text_input("Username", key="signup_username")
        new_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        if st.button("Sign Up", type="primary"):
            if new_password != confirm_password:
                st.error("Passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            elif signup_user(new_username, new_password):
                st.success("Account created successfully! Please login.")
            else:
                st.error("Username already exists")

def main_app():
    # Custom CSS for enhanced UI
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5em;
            font-weight: bold;
            background: linear-gradient(90deg, #00B4DB, #0083B0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            padding: 1rem 0;
        }
        .welcome-banner {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
        }
        .upload-section {
            background: rgba(255,255,255,0.1);
            padding: 2rem;
            border-radius: 1rem;
            border: 2px dashed #ccc;
            margin: 1rem 0;
        }
        .chat-container {
            background: white;
            border-radius: 1rem;
            padding: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .chat-message {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 0.5rem;
            color: #000000 !important;
            font-weight: 500;
        }
        .user-message {
            background-color: #e3f2fd;
            margin-left: 20%;
            border-left: 4px solid #2196f3;
        }
        .bot-message {
            background-color: #f5f5f5;
            margin-right: 20%;
            border-left: 4px solid #4caf50;
        }
        .chat-message b {
            color: #000000 !important;
        }
        .stTextInput > div > div > input {
            color: #ffffff !important;
            background-color: #333333 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="main-header">📄 PDF RAG Chatbot</div>', unsafe_allow_html=True)
    
    # Welcome banner
    st.markdown(f"""
        <div class="welcome-banner">
            <h3>Welcome, {st.session_state.username}! 👋</h3>
            <p>Upload your PDF documents and start chatting with AI to get instant answers.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.success(f"Logged in as: {st.session_state.username}")
        if st.button("Logout"):
            logout()
        
        st.markdown("---")
        
        # File uploader
        uploaded_file = st.file_uploader("Upload PDF", type="pdf")
        
        if uploaded_file:
            st.info(f"📄 {uploaded_file.name}")
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📁 Upload Section")
        if uploaded_file:
            st.success("PDF ready for processing")
    
    with col2:
        st.markdown("### 💬 Chat Interface")
        
        # Initialize session state
        if "pdf_processed" not in st.session_state:
            st.session_state.pdf_processed = False
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "pdf_name" not in st.session_state:
            st.session_state.pdf_name = ""
        
        # Process PDF
        if uploaded_file and not st.session_state.pdf_processed:
            with st.spinner("🔄 Processing PDF..."):
                text = extract_text_from_pdf(uploaded_file)
                chunks = chunk_text(text)
                embed_and_store(chunks)
                st.session_state.pdf_processed = True
                st.session_state.pdf_name = uploaded_file.name
                st.rerun()
        
        # Display PDF status
        if st.session_state.pdf_processed:
            st.info(f"📄 **Loaded:** {st.session_state.pdf_name}")
            
            # Chat interface
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f'<div class="chat-message user-message"><b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message bot-message"><b>Bot:</b> {message["content"]}</div>', unsafe_allow_html=True)
            
            # Input for new questions with automatic clearing
            with st.form(key="chat_form", clear_on_submit=True):
                question = st.text_input(
                    "Ask a question about your PDF:", 
                    key="question_input",
                    placeholder="Type your question here..."
                )
                submitted = st.form_submit_button("Send", use_container_width=True)
                
                if submitted and question:
                    with st.spinner("🤖 Thinking..."):
                        context = " ".join(retrieve_relevant_chunks(question))
                        answer = answer_question(question, context)
                        
                        st.session_state.chat_history.append({"role": "user", "content": question})
                        st.session_state.chat_history.append({"role": "bot", "content": answer})
                        st.rerun()
        else:
            st.info("Please upload a PDF to start chatting")

# Main app logic
if not st.session_state.authenticated:
    login_page()
else:
    main_app()
