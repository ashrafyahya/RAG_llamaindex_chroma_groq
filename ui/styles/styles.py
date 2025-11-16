"""
Streamlit CSS and styling configuration
"""

MODAL_CSS = """
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

def apply_styles():
    """Apply CSS styles to Streamlit app"""
    import streamlit as st
    st.markdown(MODAL_CSS, unsafe_allow_html=True)
