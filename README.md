# Agentic AI RAG System
**Status**: Active Development

A sophisticated Retrieval-Augmented Generation (RAG) system with Streamlit web interface, supporting multiple LLM providers and advanced memory management. The system enables users to upload documents, ask questions, and receive contextually accurate responses.

## Project Overview

This RAG system serves as an intelligent document assistant that combines vector search with Large Language Models to provide accurate, context-aware responses. The system features a modern web interface, document management capabilities, and conversation memory.

### Key Features

- **Multi-Provider LLM Support**: Groq, OpenAI, Google Gemini, and Deepseek APIs
- **Document Management**: Upload, delete, and manage document collections
- **Conversation Memory**: Advanced memory management with automatic summarization
- **Web Interface**: Clean, modern Streamlit-based UI with chat functionality
- **Secure Storage**: Encrypted local storage for API keys
- **Vector Search**: ChromaDB for efficient document retrieval

## Architecture

The system implements a modular RAG architecture:

1. **Document Processing**: Upload and chunk documents using LlamaIndex
2. **Vector Storage**: Store embeddings in ChromaDB with HuggingFace BGE model
3. **Query Processing**: Retrieve relevant documents and generate responses
4. **Memory Management**: Track conversation history with intelligent summarization
5. **Web Interface**: Streamlit frontend with document management and chat

## Project Structure

```
├── src/                          # Core application logic
│   ├── rag/                      # RAG system components
│   │   ├── memory_manager.py     # Conversation memory and token management
│   │   ├── rag_system.py         # Main RAG orchestrator
│   │   └── llm_query.py          # Multi-provider LLM interface
│   ├── app.py                    # Main application entry point
│   ├── chroma_setup.py           # ChromaDB initialization
│   ├── chroma_search.py          # Vector search operations
│   ├── config.py                 # Configuration settings
│   └── api_keys.py               # API key management
├── ui/                           # Streamlit web interface
│   ├── components/               # UI components
│   │   ├── chat_interface.py     # Chat UI and message handling
│   │   ├── document_management.py # File upload/delete interface
│   │   └── api_settings_modal.py # API configuration modal
│   ├── styles/                   # CSS styling
│   ├── local_storage.py          # Encrypted local storage
│   └── streamlit_app.py          # Main Streamlit application
├── chroma_db/                    # Vector database storage
└── docs/                         # Documentation
```

## Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Launch Application
```bash
streamlit run ui/streamlit_app.py
```

### 3. Configure API Keys
- Click the "API Settings" button in the sidebar
- Add your API key for at least one provider (Groq, OpenAI, Gemini, or Deepseek)
- Select your preferred provider

### 4. Upload Documents
- Use the sidebar file uploader to add documents (TXT, PDF, DOCX, MD)
- Documents are automatically processed and indexed

### 5. Start Chatting
- Ask questions about your uploaded documents
- The system retrieves relevant information and generates responses

## Supported LLM Providers

- **Groq**: Fast inference with Llama models (Default)
- **OpenAI**: GPT-3.5-turbo and GPT-4 models
- **Google Gemini**: Gemini-Pro model
- **Deepseek**: Deepseek-chat model

## Advanced Features

### Memory Management
- Automatic conversation summarization when approaching token limits
- Configurable thresholds for memory optimization
- Context preservation across long conversations

### Document Management
- Support for multiple file formats
- Duplicate detection and prevention
- Bulk document operations
- Persistent storage in ChromaDB

### Security
- Encrypted API key storage using Fernet encryption
- Local storage with user-specific encryption keys
- No API keys transmitted or logged

## Development

### Configuration
Key settings are centralized in `src/config.py`:
- `MODEL_NAME`: Default LLM model
- `TOKEN_LIMIT`: Maximum tokens per request
- `SUMMARIZE_THRESHOLD`: Memory management trigger point

### Extending LLM Support
To add new LLM providers:
1. Add provider configuration in `api_settings_modal.py`
2. Implement query function in `llm_query.py`
3. Update `APIKeyManager` in `api_keys.py`

## Future Enhancements

Planned improvements (see TODO.md):
- MongoDB integration for scalable document storage
- Enhanced sharing and collaboration features
- Cloud hosting and deployment options
- Advanced document analytics

## Technologies

- **Frontend**: Streamlit with custom CSS styling
- **Vector Database**: ChromaDB with cosine distance metric
- **Embeddings**: HuggingFace BGE-small-en-v1.5
- **LLM Integration**: Multiple provider APIs
- **Document Processing**: LlamaIndex with PyMuPDFReader for enhanced PDF handling
- **Security**: Cryptography library for key encryption
- **Memory Management**: Custom token counting and summarization
- **Relevance Filtering**: Distance-based threshold (0.7) to ensure quality responses