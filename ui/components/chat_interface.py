"""
Chat Interface Component
Handles chat display and message processing
"""
from datetime import datetime

import streamlit as st
from fpdf import FPDF

from src.app import query_documents


def initialize_chat_state():
    """Initialize chat session state"""
    if "messages" not in st.session_state:
        st.session_state.messages = []


def generate_chat_pdf():
    """Generate PDF from chat history"""
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


def show_chat_header():
    """Display chat header with action buttons"""
    col1, col2 = st.columns([4, 1])
    with col1:
        title_col = st.empty()
        if not st.session_state.show_api_modal:
            title_col.markdown('<h1 style="margin: -40px 0 0 0; padding: 0;">🤖 RAG-based AI Assistant</h1>', unsafe_allow_html=True)

    with col2:
        if st.session_state.messages and not st.session_state.show_api_modal:
            if st.button("🗑️ Clear Chat", help="Start a new chat by clearing all messages"):
                st.session_state.messages = []
                st.rerun()

            if st.download_button(
                label="📄 Download",
                data=generate_chat_pdf(),
                file_name="chat_history.pdf",
                mime="application/pdf",
                help="Download the current chat history as a PDF file"
            ):
                pass


def show_chat_interface():
    """Display chat interface"""
    if not st.session_state.show_api_modal:
        if not st.session_state.messages:
            st.header("Chat with the Assistant")

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask a question about Agentic AI..."):
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

            # Rerun to refresh the UI
            st.rerun()
