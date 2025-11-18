"""
Chat Interface Component
Handles chat display and message processing
"""
import base64
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

        # Replace problematic Unicode characters with ASCII equivalents
        # This handles common special characters that cause issues with latin-1 encoding
        content = content.replace('\u2013', '-').replace('\u2014', '--')  # en and em dashes
        content = content.replace('\u2019', "'").replace('\u2018', "'")  # smart quotes
        content = content.replace('\u201c', '"').replace('\u201d', '"')  # smart double quotes
        content = content.replace('\u2026', '...')  # ellipsis
        content = content.replace('\u00A9', '(c)').replace('\u00AE', '(R)')  # copyright and registered

        # If any non-ASCII characters remain, replace them with ?
        content = ''.join(c if ord(c) < 256 else '?' for c in content)

        pdf.multi_cell(0, 10, txt=f"{role}: {content}")
        pdf.ln(5)

    return pdf.output(dest='S').encode('latin-1')


def show_chat_header():
    """Display chat header with action buttons"""
    if not st.session_state.show_api_modal:
        st.markdown('<h1 style="margin: -40px 0 0 0; padding: 0;">🤖 RAG-based AI Assistant</h1>', unsafe_allow_html=True)


def show_fixed_chat_actions():
    """Display fixed chat action buttons on the right side"""
    import streamlit.components.v1 as components
    import base64
    
    if st.session_state.messages and not st.session_state.show_api_modal:
        # Generate PDF data for download
        pdf_data = generate_chat_pdf()
        pdf_b64 = base64.b64encode(pdf_data).decode()
        
        # Render fixed buttons with HTML/CSS
        components.html(f"""
        <style>
            .fixed-chat-actions {{
                position: fixed;
                right: 20px;
                top: 100px;
                display: flex;
                flex-direction: column;
                gap: 10px;
                z-index: 999;
            }}
            
            .chat-action-btn {{
                background: rgba(30, 41, 59, 0.95);
                border: 2px solid rgba(251, 146, 60, 0.5);
                border-radius: 12px;
                padding: 12px 20px;
                color: white;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                text-decoration: none;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                min-width: 150px;
                font-family: "Source Sans Pro", sans-serif;
            }}
            
            .chat-action-btn:hover {{
                background: rgba(45, 55, 72, 0.95);
                border-color: rgba(251, 146, 60, 0.8);
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(251, 146, 60, 0.3);
            }}
            
            .chat-action-btn:active {{
                transform: translateY(0);
            }}
        </style>
        
        <div class="fixed-chat-actions">
            <button class="chat-action-btn" onclick="clearChat()" title="Start a new chat by clearing all messages">
                🗑️ Clear Chat
            </button>
            <a class="chat-action-btn" href="data:application/pdf;base64,{pdf_b64}" download="chat_history.pdf" title="Download the current chat history as a PDF file">
                📄 Download
            </a>
        </div>
        
        <script>
            function clearChat() {{
                // Try to trigger Streamlit rerun by interacting with the session state
                // We need to communicate with the parent Streamlit app
                const parentDoc = window.parent.document;
                
                // Try to find and click a Streamlit rerun trigger
                // This is a workaround - ideally we'd use Streamlit's session state API
                window.parent.postMessage({{
                    type: 'streamlit:clearChat',
                    data: {{}}
                }}, '*');
                
                // Reload the page as a fallback
                setTimeout(function() {{
                    window.parent.location.href = window.parent.location.href.split('?')[0] + '?clear_chat=true';
                }}, 100);
            }}
        </script>
        """, height=0)


def show_chat_interface():
    """Display chat interface"""
    import streamlit.components.v1 as components

    if not st.session_state.show_api_modal:
        # Show fixed action buttons
        show_fixed_chat_actions()
        
        if not st.session_state.messages:
            st.header("Chat with the Assistant")
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
                    button_id = f"copy_btn_{message_id}"
                    # Properly escape content for data attribute
                    data_content = html.escape(content, quote=True)
                    st.markdown(
                        f"""
                        <div class="chat-message user-message" id="{message_id}">
                            <div class="message-bubble user-bubble">
                                <div class="message-content-wrapper">
                                    <div class="message-content">{escaped_content}</div>
                                    <div class="message-footer">
                                        <span class="message-timestamp">{timestamp}</span>
                                        <button class="copy-button" id="{button_id}" data-copy-text="{data_content}" title="Copy message">
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
                    button_id = f"copy_btn_{message_id}"
                    # Properly escape content for data attribute
                    data_content = html.escape(content, quote=True)
                    st.markdown(
                        f"""
                        <div class="chat-message assistant-message" id="{message_id}">
                            <div class="message-icon assistant-icon">🤖</div>
                            <div class="message-bubble assistant-bubble">
                                <div class="message-content-wrapper">
                                    <div class="message-content">{html_content}</div>
                                    <div class="message-footer">
                                        <span class="message-timestamp">{timestamp}</span>
                                        <button class="copy-button" id="{button_id}" data-copy-text="{data_content}" title="Copy message">
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
        
        # Add JavaScript to attach event listeners to copy buttons
        components.html("""
        <script>
        (function() {
            // Wait for parent document to be ready
            const attachCopyListeners = function() {
                const doc = window.parent.document;
                const copyButtons = doc.querySelectorAll('.copy-button');
                
                copyButtons.forEach(function(button) {
                    // Remove existing listeners to avoid duplicates
                    const newButton = button.cloneNode(true);
                    button.parentNode.replaceChild(newButton, button);
                    
                    // Add click event listener
                    newButton.addEventListener('click', function(e) {
                        e.preventDefault();
                        const text = this.getAttribute('data-copy-text');
                        const buttonId = this.id;
                        
                        // Use modern Clipboard API if available
                        if (navigator.clipboard && navigator.clipboard.writeText) {
                            navigator.clipboard.writeText(text).then(function() {
                                showFeedback(buttonId);
                            }).catch(function(err) {
                                console.error('Failed to copy: ', err);
                                fallbackCopy(text, buttonId);
                            });
                        } else {
                            fallbackCopy(text, buttonId);
                        }
                    });
                });
            };
            
            const fallbackCopy = function(text, buttonId) {
                const doc = window.parent.document;
                const textarea = doc.createElement('textarea');
                textarea.value = text;
                textarea.style.position = 'fixed';
                textarea.style.top = '0';
                textarea.style.left = '0';
                textarea.style.opacity = '0';
                doc.body.appendChild(textarea);
                textarea.focus();
                textarea.select();
                try {
                    doc.execCommand('copy');
                    showFeedback(buttonId);
                } catch (err) {
                    console.error('Fallback copy failed: ', err);
                }
                doc.body.removeChild(textarea);
            };
            
            const showFeedback = function(buttonId) {
                const doc = window.parent.document;
                const button = doc.getElementById(buttonId);
                if (button) {
                    const originalText = button.innerHTML;
                    button.innerHTML = '✓';
                    button.style.opacity = '1';
                    setTimeout(function() {
                        button.innerHTML = originalText;
                        button.style.opacity = '0.6';
                    }, 2000);
                }
            };
            
            // Attach listeners with a slight delay to ensure DOM is ready
            setTimeout(attachCopyListeners, 100);
        })();
        </script>
        """, height=0)

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

            # Log user message for monitoring
            print(f"User message received: {len(prompt)} characters")

            current_time = datetime.now().strftime("%H:%M")
            st.session_state.messages.append({
                "role": "user",
                "content": prompt,
                "timestamp": current_time
            })

            # Display user message immediately
            escaped_prompt = html.escape(prompt).replace('\n', '<br>')
            user_msg_id = f"msg_user_{len(st.session_state.messages)}"
            button_id = f"copy_btn_{user_msg_id}"
            data_prompt = html.escape(prompt, quote=True)
            st.markdown(
                f"""
                <div class="chat-message user-message" id="{user_msg_id}">
                    <div class="message-bubble user-bubble">
                        <div class="message-content-wrapper">
                            <div class="message-content">{escaped_prompt}</div>
                            <div class="message-footer">
                                <span class="message-timestamp">{current_time}</span>
                                <button class="copy-button" id="{button_id}" data-copy-text="{data_prompt}" title="Copy message">
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

                # Check if the response indicates errors from new pipeline
                if response.startswith("Your question is too long") or response.startswith("The conversation has become too long"):
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
            button_id = f"copy_btn_{assistant_msg_id}"
            data_response = html.escape(response, quote=True)
            st.markdown(
                f"""
                <div class="chat-message assistant-message" id="{assistant_msg_id}">
                    <div class="message-icon assistant-icon">🤖</div>
                    <div class="message-bubble assistant-bubble">
                        <div class="message-content-wrapper">
                            <div class="message-content">{html_response}</div>
                            <div class="message-footer">
                                <span class="message-timestamp">{response_time}</span>
                                <button class="copy-button" id="{button_id}" data-copy-text="{data_response}" title="Copy message">
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
            
            # Attach event listeners to newly added copy buttons
            components.html("""
            <script>
            (function() {
                const attachCopyListeners = function() {
                    const doc = window.parent.document;
                    const copyButtons = doc.querySelectorAll('.copy-button');
                    
                    copyButtons.forEach(function(button) {
                        if (button.dataset.listenerAttached) return;
                        button.dataset.listenerAttached = 'true';
                        
                        button.addEventListener('click', function(e) {
                            e.preventDefault();
                            const text = this.getAttribute('data-copy-text');
                            const buttonId = this.id;
                            
                            if (navigator.clipboard && navigator.clipboard.writeText) {
                                navigator.clipboard.writeText(text).then(function() {
                                    showFeedback(buttonId);
                                }).catch(function(err) {
                                    console.error('Failed to copy: ', err);
                                    fallbackCopy(text, buttonId);
                                });
                            } else {
                                fallbackCopy(text, buttonId);
                            }
                        });
                    });
                };
                
                const fallbackCopy = function(text, buttonId) {
                    const doc = window.parent.document;
                    const textarea = doc.createElement('textarea');
                    textarea.value = text;
                    textarea.style.position = 'fixed';
                    textarea.style.top = '0';
                    textarea.style.left = '0';
                    textarea.style.opacity = '0';
                    doc.body.appendChild(textarea);
                    textarea.focus();
                    textarea.select();
                    try {
                        doc.execCommand('copy');
                        showFeedback(buttonId);
                    } catch (err) {
                        console.error('Fallback copy failed: ', err);
                    }
                    doc.body.removeChild(textarea);
                };
                
                const showFeedback = function(buttonId) {
                    const doc = window.parent.document;
                    const button = doc.getElementById(buttonId);
                    if (button) {
                        const originalText = button.innerHTML;
                        button.innerHTML = '✓';
                        button.style.opacity = '1';
                        setTimeout(function() {
                            button.innerHTML = originalText;
                            button.style.opacity = '0.6';
                        }, 2000);
                    }
                };
                
                setTimeout(attachCopyListeners, 100);
            })();
            </script>
            """, height=0)

            # Auto-scroll to bottom and refocus input
            components.html("""
            <script>
            (function() {
                function scrollAndFocus() {
                    const doc = window.parent.document;
                    
                    // Scroll to bottom
                    window.parent.scrollTo({ 
                        top: doc.body.scrollHeight, 
                        behavior: 'smooth' 
                    });
                    
                    // Refocus the chat input with multiple selectors
                    setTimeout(function() {
                        const chatInput = doc.querySelector('[data-testid="stChatInput"] input') ||
                                        doc.querySelector('input[type="text"]') ||
                                        doc.querySelector('.stChatInput input');
                        if (chatInput) {
                            chatInput.focus();
                            chatInput.click();
                        }
                    }, 300);
                }
                
                // Try multiple times to ensure focus
                scrollAndFocus();
                setTimeout(scrollAndFocus, 500);
                setTimeout(scrollAndFocus, 1000);
            })();
            </script>
            """, height=0)

            # Rerun to refresh the UI
            st.rerun()

    # Ensure chat input is focused when page loads or updates
    if not st.session_state.is_thinking:
        components.html("""
        <script>
        (function() {
            function focusInput() {
                const doc = window.parent.document;
                const chatInput = doc.querySelector('[data-testid="stChatInput"] input') ||
                                doc.querySelector('input[type="text"]') ||
                                doc.querySelector('.stChatInput input');
                if (chatInput) {
                    chatInput.focus();
                    chatInput.click();
                }
            }
            
            // Focus immediately and retry
            focusInput();
            setTimeout(focusInput, 100);
            setTimeout(focusInput, 300);
            setTimeout(focusInput, 500);
        })();
        </script>
        """, height=0)


