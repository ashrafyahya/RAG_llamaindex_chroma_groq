import os
import sys

import streamlit as st

# Add the src directory to the path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.app import load_documents, query_documents

# Set page config
st.set_page_config(page_title="RAG-based AI Assistant", page_icon="🤖")

# Title
st.title("🤖 RAG-based AI Assistant")

# Sidebar for document loading
with st.sidebar:
    st.header("Document Management")
    if st.button("Load Documents"):
        with st.spinner("Loading documents into ChromaDB..."):
            load_documents()
        st.success("Documents loaded successfully!")

# Chat interface
st.header("Chat with the Assistant")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about Agentic AI..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from the assistant
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = query_documents(prompt)
        st.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
