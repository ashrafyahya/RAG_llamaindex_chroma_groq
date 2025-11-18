"""
Streamlit RAG-based AI Assistant Application
Main entry point for the UI
"""
import os
import sys

import streamlit as st

# Add the parent directory and src directory to the path
parent_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'src'))

from ui.components.api_settings_modal import (initialize_api_settings_state,
                                              show_api_settings_modal)
from ui.components.chat_interface import (initialize_chat_state,
                                          show_chat_header,
                                          show_chat_interface)
from ui.components.document_management import show_document_management_sidebar
from ui.local_storage import get_storage
from ui.styles.styles import apply_styles

# Set page config with wide layout
st.set_page_config(
    page_title="RAG-based AI Assistant", 
    page_icon="🤖",
    layout="centered"
)

# Initialize storage
storage = get_storage()

# Apply CSS styles
apply_styles()

# Initialize all session states
initialize_api_settings_state()
initialize_chat_state()

# Render document management in sidebar
show_document_management_sidebar()
    
# Show API Settings Modal if toggled
if st.session_state.show_api_modal:
    show_api_settings_modal()
else:

    # Render chat header
    show_chat_header()

    # Render chat interface
    show_chat_interface()

