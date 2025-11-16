import importlib
import os
import sys
from datetime import datetime

import streamlit as st
from fpdf import FPDF

# Add the src directory to the path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from local_storage import get_storage

from src.api_keys import APIKeyManager
from src.app import (clear_all_documents, delete_document,
                     get_uploaded_documents, query_documents, upload_document)

# Force reload of api_keys module to ensure latest version is loaded
if 'src.api_keys' in sys.modules:
    importlib.reload(sys.modules['src.api_keys'])
    from src.api_keys import APIKeyManager

# Set page config
st.set_page_config(page_title="RAG-based AI Assistant", page_icon="🤖")

# Initialize local storage
storage = get_storage()

# Initialize session state for API keys and modal
if "api_keys" not in st.session_state:
    # Load from local storage
    stored_keys = storage.load_api_keys()
    st.session_state.api_keys = stored_keys

if "show_api_modal" not in st.session_state:
    st.session_state.show_api_modal = False

if "selected_api_provider" not in st.session_state:
    # Load from local storage
    st.session_state.selected_api_provider = storage.load_selected_provider()

if "api_modal_tab_changed" not in st.session_state:
    st.session_state.api_modal_tab_changed = False

if "api_key_reset_counter" not in st.session_state:
    st.session_state.api_key_reset_counter = {}

# CSS for modal styling
modal_css = """
<style>
    [data-testid="stModal"] {
        z-index: 999 !important;
    }
    
    div[data-modal="true"] {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 999;
    }
    
    /* Hide the eye icon (show/hide password toggle) */
    input[type="password"]::after,
    input[type="password"] ~ button {
        display: none !important;
    }
    
    /* Disable text selection on password fields */
    input[type="password"] {
        user-select: none !important;
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
    }
    
    /* Reduce spacing in modal */
    [data-testid="stContainer"] [data-testid="element-container"] {
        margin-bottom: 0.5rem;
    }
    
    /* Reduce divider margin */
    hr {
        margin: 1rem 0 !important;
    }
    
    /* Reduce heading margins */
    h3 {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .api-key-container {
        position: relative;
        display: flex;
        align-items: center;
    }
    
    .api-key-input {
        padding-right: 40px !important;
    }
    
    .api-key-clear-btn {
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        background: none;
        border: none;
        cursor: pointer;
        font-size: 18px;
        color: #888;
        padding: 0;
        margin: 0;
        z-index: 10;
    }
    
    .api-key-clear-btn:hover {
        color: #fff;
    }
</style>
"""

st.markdown(modal_css, unsafe_allow_html=True)

# Function to render API Settings Modal
def show_api_settings_modal():
    # Create a centered modal-like container
    col1, col2, col3 = st.columns([0.2, 2.1, 0.4])
    
    with col2:
        # Modal container with border and background
        with st.container(border=True):
            # Modal header
            col_header1, col_header2 = st.columns([5, 1])
            with col_header1:
                st.markdown("<h2 style='margin: 0; padding: 0;'>⚙️ API Keys Configuration</h2>", unsafe_allow_html=True)
            with col_header2:
                if st.button("✕", key="close_modal", help="Close settings"):
                    st.session_state.show_api_modal = False
                    st.rerun()
            
            st.divider()
            
            # Provider selector - more reliable than tabs for detecting user selection
            providers = ["Groq", "OpenAI", "Gemini", "Deepseek"]
            provider_keys = ["groq", "openai", "gemini", "deepseek"]
            provider_urls = [
                "https://console.groq.com",
                "https://platform.openai.com/api-keys",
                "https://ai.google.dev",
                "https://platform.deepseek.com"
            ]
            
            # Find current index
            try:
                current_index = provider_keys.index(st.session_state.selected_api_provider)
            except ValueError:
                current_index = 0
            
            # Use columns to mimic tabs with buttons for provider selection
            provider_cols = st.columns(4)
            for i, (col, provider_name, provider_key) in enumerate(zip(provider_cols, providers, provider_keys)):
                with col:
                    # Button styling to show active provider
                    button_label = f"✓ {provider_name}" if provider_key == st.session_state.selected_api_provider else provider_name
                    if st.button(button_label, use_container_width=True, key=f"provider_btn_{provider_key}"):
                        st.session_state.selected_api_provider = provider_key
                        st.rerun()
            
            st.divider()
            
            # Display API key input for the selected provider
            selected_provider_idx = provider_keys.index(st.session_state.selected_api_provider)
            selected_provider_name = providers[selected_provider_idx]
            selected_provider_url = provider_urls[selected_provider_idx]
            
            # Title with reset button
            col_title, col_reset = st.columns([0.9, 0.1])
            with col_title:
                st.markdown(f"<h3 style='margin: 0; padding: 0;'>Enter your {selected_provider_name} API Key</h3>", unsafe_allow_html=True)
            with col_reset:
                if st.button("X", key=f"reset_{st.session_state.selected_api_provider}", help="Clear API key from input and storage"):
                    # Clear from session state
                    st.session_state.api_keys[st.session_state.selected_api_provider] = ""
                    # Clear from local storage
                    storage.save_api_keys(st.session_state.api_keys)
                    # Increment reset counter to force widget re-initialization
                    if st.session_state.selected_api_provider not in st.session_state.api_key_reset_counter:
                        st.session_state.api_key_reset_counter[st.session_state.selected_api_provider] = 0
                    st.session_state.api_key_reset_counter[st.session_state.selected_api_provider] += 1
                    st.rerun()
            
            current_value = st.session_state.api_keys.get(st.session_state.selected_api_provider, "")
            
            # Get reset counter for dynamic key
            reset_count = st.session_state.api_key_reset_counter.get(st.session_state.selected_api_provider, 0)
            
            # Display API key input with dynamic key based on reset counter
            new_value = st.text_input(
                "API Key",
                value=current_value,
                type="password",
                help=f"Get your API key from {selected_provider_url}",
                key=f"{st.session_state.selected_api_provider}_input_{reset_count}"
            )
            if new_value != current_value:
                st.session_state.api_keys[st.session_state.selected_api_provider] = new_value
            
            st.divider()
            
            # Display currently active provider
            st.markdown(f"**Current Active Provider:** `{st.session_state.selected_api_provider.upper()}`")
            
            # Close button
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                if st.button("Save & Close", use_container_width=True, key="save_close_btn"):
                    # Save API keys and selected provider to local storage
                    storage.save_api_keys(st.session_state.api_keys)
                    storage.save_selected_provider(st.session_state.selected_api_provider)
                    st.success("✅ API keys saved!")
                    st.session_state.show_api_modal = False
                    st.rerun()

# Title with clear chat button inline - always render but use CSS to control visibility
col1, col2 = st.columns([4, 1])
with col1:
    title_col = st.empty()
    if not st.session_state.show_api_modal:
        title_col.markdown('<h1 style="margin: -40px 0 0 0; padding: 0;">🤖 RAG-based AI Assistant</h1>', unsafe_allow_html=True)

with col2:
    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Button to clear chat history - only show if there are messages and modal is closed
    if st.session_state.messages and not st.session_state.show_api_modal:
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

# Show API Settings Modal if toggled
if st.session_state.show_api_modal:
    show_api_settings_modal()

# Sidebar for document management
with st.sidebar:
    st.markdown("<h2 style='margin: -50px 0 0 0; padding: 0;'>Document Management</h2>", unsafe_allow_html=True)

    # API Settings button - always visible
    if st.button("⚙️ API Settings", help="Configure your API keys", use_container_width=True):
        st.session_state.show_api_modal = not st.session_state.show_api_modal
        st.rerun()

    # Fetch uploaded documents to check if any exist
    uploaded_docs = get_uploaded_documents()

    # Clear all button - only show if there are uploaded documents
    if uploaded_docs:
        if st.button("🗑️ Clear database", help="Remove all documents from database", use_container_width=True):
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

# Chat interface - only show if modal is not open
if not st.session_state.show_api_modal:
    if not st.session_state.messages:
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
                response = query_documents(
                    prompt,
                    api_provider=st.session_state.selected_api_provider,
                    api_key_groq=st.session_state.api_keys["groq"],
                    api_key_openai=st.session_state.api_keys["openai"],
                    api_key_gemini=st.session_state.api_keys["gemini"],
                    api_key_deepseek=st.session_state.api_keys["deepseek"]
                )
            st.markdown(response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Rerun to refresh the UI and show the clear button immediately
        st.rerun()
