import os
import sys
from datetime import datetime

import streamlit as st
from fpdf import FPDF

# Add the src directory to the path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.app import (clear_all_documents, delete_document,
                     get_uploaded_documents, query_documents, upload_document)

# Set page config
st.set_page_config(page_title="RAG-based AI Assistant", page_icon="🤖")

# Title with clear chat button inline
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🤖 RAG-based AI Assistant")
with col2:
    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Button to clear chat history - only show if there are messages
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat", help="Start a new chat by clearing all messages"):
            st.session_state.messages = []
            st.rerun()

        # Function to generate PDF from chat history
        def generate_chat_pdf():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            pdf.cell(200, 10, txt="Chat History", ln=True, align='C')
            pdf.set_font("Arial", size=10)
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pdf.cell(200, 10, txt=f"Generated on: {current_date}", ln=True, align='C')
            pdf.ln(10)

            pdf.set_font("Arial", size=12)
            for message in st.session_state.messages:
                role = message["role"].capitalize()
                content = message["content"]
                pdf.multi_cell(0, 10, txt=f"{role}: {content}")
                pdf.ln(5)

            return pdf.output(dest='S').encode('latin-1')

        # Download button for chat history as PDF
        if st.download_button(
            label="📄 Download",
            data=generate_chat_pdf(),
            file_name="chat_history.pdf",
            mime="application/pdf",
            help="Download the current chat history as a PDF file"
        ):
            pass  # Button action handled by download_button

# Sidebar for document management
with st.sidebar:
    st.markdown("<h2 style='margin: 0; padding: 0;'>Document Management</h2>", unsafe_allow_html=True)

    # Fetch uploaded documents to check if any exist
    uploaded_docs = get_uploaded_documents()

    # Management buttons in same line - only show if there are uploaded documents
    if uploaded_docs:
        col1 = st.columns(1)[0]
        with col1:
            if st.button("🗑️ Clear all uploaded documents", help="Remove all documents from database"):
                with st.spinner("Clearing all documents..."):
                    result = clear_all_documents()
                    if "Successfully" in result:
                        st.success(result)
                        st.rerun()
                    else:
                        st.error(result)

    # File uploader with dynamic key to clear after upload
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    uploaded_files = st.file_uploader("Upload documents", type=['txt', 'pdf', 'docx', 'md'], accept_multiple_files=True, key=f"uploader_{st.session_state.uploader_key}")
    if uploaded_files:
        if st.button("Upload Documents"):
            with st.spinner("Uploading and indexing documents..."):
                success_count = 0
                error_messages = []
                for uploaded_file in uploaded_files:
                    result = upload_document(uploaded_file)
                    if "Successfully" in result:
                        success_count += 1
                    else:
                        error_messages.append(result)
                if success_count > 0:
                    st.success(f"Successfully uploaded {success_count} document(s)")
                    # Clear the uploader by changing the key
                    st.session_state.uploader_key += 1
                    st.rerun()
                if error_messages:
                    for error in error_messages:
                        st.error(error)


    # Display uploaded documents
    st.subheader("Uploaded Documents:")

    if uploaded_docs:
        for doc in uploaded_docs:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{doc['name']}**")
            with col2:
                st.write(f"{doc['size'] / 1024:.2f} KB")
            with col3:
                # Delete all chunks of this document
                if st.button("🗑️", key=f"delete_{doc['ids'][0]}"):
                    deleted_count = 0
                    for doc_id in doc['ids']:
                        result = delete_document(doc_id)
                        if "successfully" in result.lower():
                            deleted_count += 1
                    if deleted_count == len(doc['ids']):
                        st.success(f"Document '{doc['name']}' deleted successfully!")
                        st.rerun()  # Refresh to show updated list
                    else:
                        st.error(f"Error deleting some chunks of '{doc['name']}'")
    else:
        st.write("No uploaded documents yet.")

# Chat interface
st.header("Chat with the Assistant")

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

    # Rerun to refresh the UI and show the clear button immediately
    st.rerun()
