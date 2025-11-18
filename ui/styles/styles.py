"""
Streamlit CSS Styling Module

Provides comprehensive CSS styling for the RAG system web interface,
including modal styling, chat message bubbles, animations, and responsive design.
"""

MODAL_CSS = """
<style>
    /* Set minimum width of sidebar to 15% */
    .css-1d391kg {
        min-width: 15% !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 15% !important;
    }
    
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

    /* Hide link icons beside headers */
    h1 a, h2 a, h3 a {
        display: none !important;
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
    
    /* Chat message container with enhanced animations */
    .chat-message {
        margin: 1.25rem 0;
        display: flex;
        width: 100%;
        animation: slideInFade 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        # scroll-margin-top: 20px;
    }
    
    @keyframes slideInFade {
        from {
            opacity: 0;
            transform: translateY(15px) scale(0.98);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    /* User messages - right aligned with margin */
    .user-message {
        display: flex;
        align-items: flex-start;
        justify-content: flex-end;
        gap: 0.75rem;
        padding-right: 0.5rem;
    }
    
    /* Assistant messages - left aligned with margin */
    .assistant-message {
        display: flex;
        align-items: flex-start;
        justify-content: flex-start;
        gap: 0.75rem;
        padding-left: 0.5rem;
    }
    
    /* Message bubble container with enhanced styling */
    .message-bubble {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        padding: 1.5rem 1.0rem;
        word-wrap: break-word;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    
    .message-bubble:hover {
        transform: translateY(-2px) scale(1.01);
    }
    
    /* User message bubble - stronger visual hierarchy */
    .user-bubble {
        background: rgba(74, 85, 104, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.5);
        border-radius: 20px 20px 6px 20px;
        flex-direction: row;
        width: 80%;
        min-width: 80%;
        max-width: 80%;
        box-shadow: 0 4px 12px rgba(74, 85, 104, 0.15),
                    0 2px 6px rgba(74, 85, 104, 0.1),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    
    .user-bubble:hover {
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.2), 
                    0 3px 8px rgba(239, 68, 68, 0.15),
                    inset 0 1px 0 rgba(255, 255, 255, 0.08);
        border-color: rgba(239, 68, 68, 0.65);
    }
    
    /* Assistant message bubble - distinct from user */
    .assistant-bubble {
        background: rgba(45, 55, 72, 0.1);
        border: 1px solid rgba(251, 146, 60, 0.5);
        border-radius: 20px 20px 20px 6px;
        flex-direction: row;
        width: 80%;
        min-width: 80%;
        max-width: 80%;
        box-shadow: 0 4px 12px rgba(45, 55, 72, 0.15),
                    0 2px 6px rgba(45, 55, 72, 0.1),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    
    .assistant-bubble:hover {
        box-shadow: 0 6px 20px rgba(251, 146, 60, 0.2), 
                    0 3px 8px rgba(251, 146, 60, 0.15),
                    inset 0 1px 0 rgba(255, 255, 255, 0.08);
        border-color: rgba(251, 146, 60, 0.65);
    }
    
    /* Message icon/avatar with enhanced styling - positioned outside bubble */
    .message-icon {
        font-size: 1.75rem;
        flex-shrink: 0;
        margin-top: 0.5rem;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 2.5rem;
        height: 2.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        backdrop-filter: blur(10px);
        order: -1;
    }
    
    .user-message .message-icon {
        order: 1;
    }
    
    .assistant-message .message-icon {
        order: -1;
    }
    
    .chat-message:hover .message-icon {
        transform: scale(1.1);
    }
    
    .user-icon {
        color: #ef4444;
        filter: drop-shadow(0 2px 4px rgba(239, 68, 68, 0.4));
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.15));
    }
    
    .assistant-icon {
        color: #fb923c;
        filter: drop-shadow(0 2px 4px rgba(251, 146, 60, 0.4));
        background: linear-gradient(135deg, rgba(251, 146, 60, 0.2), rgba(249, 115, 22, 0.15));
    }
    
    /* Message content wrapper */
    .message-content-wrapper {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }
    
    /* Message content with improved typography */
    .message-content {
        flex: 1;
        line-height: 1.85;
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.05rem;
        letter-spacing: 0.015em;
        font-weight: 400;
        font-family: 'Times New Roman', Times, serif; /* Formal German-style font */
    }
    
    .message-content p {
        margin: 0.625rem 0;
    }
    
    .message-content p:first-child {
        margin-top: 0;
    }
    
    .message-content p:last-child {
        margin-bottom: 0;
    }
    
    /* Message footer with cleaner timestamp and copy button */
    .message-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        opacity: 0.8;
        transition: opacity 0.3s ease;
    }
    
    .message-bubble:hover .message-footer {
        opacity: 1;
        border-top-color: rgba(255, 255, 255, 0.12);
    }
    
    .message-timestamp {
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.5);
        font-weight: 500;
        letter-spacing: 0.5px;
        font-variant-numeric: tabular-nums;
    }
    
    .copy-button {
        background: transparent;
        border: none;
        cursor: pointer;
        font-size: 0.875rem;
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
        opacity: 0.6;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .copy-button:hover {
        opacity: 1;
        background: rgba(255, 255, 255, 0.1);
        transform: scale(1.1);
    }
    
    .copy-button:active {
        transform: scale(0.95);
    }
    
    /* Markdown elements within messages - enhanced */
    .message-content code {
        background: rgba(0, 0, 0, 0.25);
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
        font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
        font-size: 0.875em;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #fbbf24;
    }
    
    .message-content strong {
        font-weight: 600;
        color: rgba(255, 255, 255, 0.95);
    }
    
    .message-content em {
        font-style: italic;
        color: rgba(255, 255, 255, 0.9);
    }
    
    /* Smooth scrolling for chat container */
    .chat-container {
        scroll-behavior: smooth;
    }
    
    /* Loading indicator styling */
    .stSpinner > div {
        border-color: #fb923c transparent transparent transparent !important;
    }
    
    /* Modern input area styling */
    [data-testid="stChatInput"] {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 2px solid rgba(251, 146, 60, 0.3) !important;
        border-radius: 16px !important;
        padding: 1.25rem 0.5rem !important;
    }
    
    [data-testid="stChatInput"]:focus-within {
        border-color: rgba(251, 146, 60, 0.6) !important;
        box-shadow: 0 6px 20px rgba(251, 146, 60, 0.2), 
                    0 3px 8px rgba(251, 146, 60, 0.15),
                    inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
        transform: translateY(-1px) !important;
    }
</style>
"""

def apply_styles():
    """
    Apply comprehensive CSS styles to the Streamlit application.
    
    This function injects custom CSS for:
    - Chat message styling with animations
    - Modal and sidebar layouts
    - Button and input field enhancements
    - Security features (password field protection)
    - Responsive design elements
    """
    import streamlit as st
    st.markdown(MODAL_CSS, unsafe_allow_html=True)
