"""
API Settings Modal Component
Handles API key configuration UI
"""
import streamlit as st

from ui.local_storage import get_storage

# Provider configuration
PROVIDERS = {
    "groq": {
        "name": "Groq",
        "url": "https://console.groq.com"
    },
    "openai": {
        "name": "OpenAI",
        "url": "https://platform.openai.com/api-keys"
    },
    "gemini": {
        "name": "Gemini",
        "url": "https://ai.google.dev"
    },
    "deepseek": {
        "name": "Deepseek",
        "url": "https://platform.deepseek.com"
    }
}

PROVIDER_LIST = list(PROVIDERS.keys())
PROVIDER_NAMES = [PROVIDERS[p]["name"] for p in PROVIDER_LIST]
PROVIDER_URLS = [PROVIDERS[p]["url"] for p in PROVIDER_LIST]


def initialize_api_settings_state():
    """Initialize session state for API settings"""
    storage = get_storage()
    
    if "api_keys" not in st.session_state:
        stored_keys = storage.load_api_keys()
        st.session_state.api_keys = stored_keys

    if "show_api_modal" not in st.session_state:
        st.session_state.show_api_modal = False

    if "selected_api_provider" not in st.session_state:
        st.session_state.selected_api_provider = storage.load_selected_provider()

    if "api_key_reset_counter" not in st.session_state:
        st.session_state.api_key_reset_counter = {}


def show_api_settings_modal():
    """Render API Settings Modal"""
    storage = get_storage()
    
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
            
            # Provider selector buttons
            provider_cols = st.columns(4)
            for i, (col, provider_name, provider_key) in enumerate(zip(provider_cols, PROVIDER_NAMES, PROVIDER_LIST)):
                with col:
                    button_label = f"✓ {provider_name}" if provider_key == st.session_state.selected_api_provider else provider_name
                    if st.button(button_label, use_container_width=True, key=f"provider_btn_{provider_key}"):
                        st.session_state.selected_api_provider = provider_key
                        st.rerun()
            
            st.divider()
            
            # Display API key input for the selected provider
            selected_provider_idx = PROVIDER_LIST.index(st.session_state.selected_api_provider)
            selected_provider_name = PROVIDER_NAMES[selected_provider_idx]
            selected_provider_url = PROVIDER_URLS[selected_provider_idx]
            
            # Title with reset button
            col_title, col_reset = st.columns([0.9, 0.1])
            with col_title:
                st.markdown(f"<h3 style='margin: 0; padding: 0;'>Enter your {selected_provider_name} API Key</h3>", unsafe_allow_html=True)
            with col_reset:
                if st.button("X", key=f"reset_{st.session_state.selected_api_provider}", help="Clear API key from input and storage"):
                    st.session_state.api_keys[st.session_state.selected_api_provider] = ""
                    storage.save_api_keys(st.session_state.api_keys)
                    if st.session_state.selected_api_provider not in st.session_state.api_key_reset_counter:
                        st.session_state.api_key_reset_counter[st.session_state.selected_api_provider] = 0
                    st.session_state.api_key_reset_counter[st.session_state.selected_api_provider] += 1
                    st.rerun()
            
            current_value = st.session_state.api_keys.get(st.session_state.selected_api_provider, "")
            reset_count = st.session_state.api_key_reset_counter.get(st.session_state.selected_api_provider, 0)
            
            # Display API key input
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
                    storage.save_api_keys(st.session_state.api_keys)
                    storage.save_selected_provider(st.session_state.selected_api_provider)
                    st.success("✅ API keys saved!")
                    st.session_state.show_api_modal = False
                    st.rerun()
