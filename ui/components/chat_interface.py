"""
Chat Interface Component
Handles chat display and message processing
"""
import html
import re
from datetime import datetime

import streamlit as st
from fpdf import FPDF

from src.app import clear_chat_memory, query_documents


def markdown_to_html(text):
    """Convert basic markdown to HTML"""
    # Escape HTML first
    text = html.escape(text)

    # Convert markdown patterns to HTML
    # Bold: **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)

    # Italic: *text* or _text_
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'<em>\1</em>', text)

    # Code: `text`
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    # Line breaks
    text = text.replace('\n', '<br>')

    return text


def initialize_chat_state():
    """Initialize chat session state"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "is_thinking" not in st.session_state:
        st.session_state.is_thinking = False
    if "user_input" not in st.session_state:
        st.session_state.user_input = None


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
                clear_chat_memory()
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
    # Add JavaScript for copy functionality
    st.markdown("""
    <script>
    function copyToClipboard(messageId, text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand('copy');
            // Visual feedback
            const button = document.querySelector('#' + messageId + ' .copy-button');
            if (button) {
                const originalText = button.innerHTML;
                button.innerHTML = '✓';
                button.style.opacity = '1';
                setTimeout(function() {
                    button.innerHTML = originalText;
                }, 2000);
            }
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
        document.body.removeChild(textarea);
    }
    </script>
    """, unsafe_allow_html=True)

    if not st.session_state.show_api_modal:
        if not st.session_state.messages:
            st.header("Chat with the Assistant")

        # Display chat history with custom alternating layout
        chat_container = st.container()
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        with chat_container:
            for idx, message in enumerate(st.session_state.messages):
                role = message["role"]
                content = message["content"]

                # Get timestamp if available, otherwise use current time
                timestamp = message.get("timestamp", datetime.now().strftime("%H:%M"))
                message_id = f"msg_{idx}"

                # Determine alignment: user = right, assistant = left
                if role == "user":
                    # User message on the right - plain text with human icon outside on the right
                    escaped_content = html.escape(content).replace('\n', '<br>')
                    # Escape content for JavaScript (handle quotes and newlines)
                    js_content = content.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
                    st.markdown(
                        f"""
                        <div class="chat-message user-message" id="{message_id}">
                            <div class="message-bubble user-bubble">
                                <div class="message-content-wrapper">
                                    <div class="message-content">{escaped_content}</div>
                                    <div class="message-footer">
                                        <span class="message-timestamp">{timestamp}</span>
                                        <button class="copy-button" onclick="copyToClipboard('{message_id}', {repr(js_content)})" title="Copy message">
                                            📋
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div class="message-icon user-icon">👤</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    # Assistant message on the left - with markdown support and robot icon outside on the left
                    html_content = markdown_to_html(content)
                    # Escape content for JavaScript (handle quotes and newlines)
                    js_content = content.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
                    st.markdown(
                        f"""
                        <div class="chat-message assistant-message" id="{message_id}">
                            <div class="message-icon assistant-icon">🤖</div>
                            <div class="message-bubble assistant-bubble">
                                <div class="message-content-wrapper">
                                    <div class="message-content">{html_content}</div>
                                    <div class="message-footer">
                                        <span class="message-timestamp">{timestamp}</span>
                                        <button class="copy-button" onclick="copyToClipboard('{message_id}', {repr(js_content)})" title="Copy message">
                                            📋
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        st.markdown('</div>', unsafe_allow_html=True)

        # Chat input 
        # Check if model is thinking before rendering input
        if st.session_state.is_thinking:
            # Show disabled input when model is thinking
            st.chat_input("Model is responding...", disabled=True)
        else:
            # Only enable input when model is not thinking
            prompt = st.chat_input("Type your message here...")
            if prompt:
                # Set thinking state to True immediately after user sends message
                st.session_state.is_thinking = True
                st.session_state.user_input = prompt  # Store the input
                st.rerun()  # Rerun to update the UI immediately

        # Check if there's stored user input to process
        if st.session_state.user_input:
            # Retrieve and clear the stored input
            prompt = st.session_state.user_input
            st.session_state.user_input = None

            # Debug output for every user message
            print(f"[CHAT_DEBUG] User sent message: '{prompt}' (length: {len(prompt)} chars)")

            current_time = datetime.now().strftime("%H:%M")
            st.session_state.messages.append({
                "role": "user",
                "content": prompt,
                "timestamp": current_time
            })

            # Display user message immediately
            escaped_prompt = html.escape(prompt).replace('\n', '<br>')
            user_msg_id = f"msg_user_{len(st.session_state.messages)}"
            js_prompt = prompt.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
            st.markdown(
                f"""
                <div class="chat-message user-message" id="{user_msg_id}">
                    <div class="message-bubble user-bubble">
                        <div class="message-content-wrapper">
                            <div class="message-content">{escaped_prompt}</div>
                            <div class="message-footer">
                                <span class="message-timestamp">{current_time}</span>
                                <button class="copy-button" onclick="copyToClipboard('{user_msg_id}', {repr(js_prompt)})" title="Copy message">
                                    📋
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="message-icon user-icon">👤</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Get response from the assistant
            with st.spinner("Thinking..."):
                response = query_documents(
                    prompt,
                    api_provider=st.session_state.selected_api_provider,
                    api_key_groq=st.session_state.api_keys["groq"],
                    api_key_openai=st.session_state.api_keys["openai"],
                    api_key_gemini=st.session_state.api_keys["gemini"],
                    api_key_deepseek=st.session_state.api_keys["deepseek"]
                )

                # Check if the response indicates an error
                if response.startswith("Your question is too long"):
                    st.error(response)
                    # Remove the user message from the history since it wasn't processed
                    st.session_state.messages.pop()
                    st.session_state.is_thinking = False  # Reset thinking state
                    st.rerun()
                    return

            # Display assistant response with markdown rendering
            response_time = datetime.now().strftime("%H:%M")
            html_response = markdown_to_html(response)
            assistant_msg_id = f"msg_assistant_{len(st.session_state.messages) + 1}"
            js_response = response.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
            st.markdown(
                f"""
                <div class="chat-message assistant-message" id="{assistant_msg_id}">
                    <div class="message-icon assistant-icon">🤖</div>
                    <div class="message-bubble assistant-bubble">
                        <div class="message-content-wrapper">
                            <div class="message-content">{html_response}</div>
                            <div class="message-footer">
                                <span class="message-timestamp">{response_time}</span>
                                <button class="copy-button" onclick="copyToClipboard('{assistant_msg_id}', {repr(js_response)})" title="Copy message">
                                    📋
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": response_time
            })

            # Reset thinking state to False
            st.session_state.is_thinking = False

            # Auto-scroll to bottom
            st.markdown("""
            <script>
            setTimeout(function() {
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            }, 100);
            </script>
            """, unsafe_allow_html=True)

            # Rerun to refresh the UI
            st.rerun()
