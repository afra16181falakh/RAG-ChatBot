import streamlit as st
from pdf_utils import extract_text_from_pdf
from rag_utils import chunk_text, embed_and_store, retrieve_relevant_chunks, answer_question

st.set_page_config(page_title="PDF RAG Chatbot", layout="wide")
st.title("📄 PDF RAG Chatbot")

if "pdf_processed" not in st.session_state:
    st.session_state.pdf_processed = False

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file and not st.session_state.pdf_processed:
    with st.spinner("Extracting text from PDF..."):
        text = extract_text_from_pdf(uploaded_file)
        chunks = chunk_text(text)
        embed_and_store(chunks)
        st.session_state.pdf_processed = True
        st.success("PDF processed! You can now ask questions.")

if st.session_state.pdf_processed:
    question = st.text_input("Ask a question about your PDF:")
    if question:
        with st.spinner("Retrieving answer..."):
            context = " ".join(retrieve_relevant_chunks(question))
            answer = answer_question(question, context)
            st.markdown(f"**Answer:** {answer}")