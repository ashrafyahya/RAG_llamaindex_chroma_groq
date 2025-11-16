"""
Document Management Component
Handles file uploads, deletion, and document listing
"""
import streamlit as st

from src.app import (clear_all_documents, delete_document,
                     get_uploaded_documents, upload_document)


def show_document_management_sidebar():
    """Render document management in sidebar"""
    with st.sidebar:
        st.markdown("<h2 style='margin: -50px 0 0 0; padding: 0;'>Document Management</h2>", unsafe_allow_html=True)

        # API Settings button
        if st.button("⚙️ API Settings", help="Configure your API keys", use_container_width=True):
            st.session_state.show_api_modal = not st.session_state.show_api_modal
            st.rerun()

        # Fetch uploaded documents
        uploaded_docs = get_uploaded_documents()

        # Clear all button
        if uploaded_docs:
            if st.button("🗑️ Clear database", help="Remove all documents from database", use_container_width=True):
                with st.spinner("Clearing all documents..."):
                    result = clear_all_documents()
                    if "Successfully" in result:
                        st.success(result)
                        st.rerun()
                    else:
                        st.error(result)

        # File uploader
        if "uploader_key" not in st.session_state:
            st.session_state.uploader_key = 0

        uploaded_files = st.file_uploader(
            "Upload documents",
            type=['txt', 'pdf', 'docx', 'md'],
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.uploader_key}"
        )
        
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
                    if st.button("🗑️", key=f"delete_{doc['ids'][0]}"):
                        deleted_count = 0
                        for doc_id in doc['ids']:
                            result = delete_document(doc_id)
                            if "successfully" in result.lower():
                                deleted_count += 1
                        if deleted_count == len(doc['ids']):
                            st.success(f"Document '{doc['name']}' deleted successfully!")
                            st.rerun()
                        else:
                            st.error(f"Error deleting some chunks of '{doc['name']}'")
        else:
            st.write("No uploaded documents yet.")
