# Agentic AI RAG System
**Status**: Active Development

A sophisticated Retrieval-Augmented Generation (RAG) system with React Ionic frontend and FastAPI backend, supporting multiple LLM providers and advanced memory management. The system enables users to upload documents, ask questions, and receive contextually accurate responses.

## Project Overview

This RAG system serves as an intelligent document assistant that combines vector search with Large Language Models to provide accurate, context-aware responses. The system features a modern web interface built with React Ionic, REST API backend, document management capabilities, and conversation memory.

### Key Features

- **Multi-Provider LLM Support**: Groq, OpenAI, Google Gemini, and Deepseek APIs
- **Document Management**: Upload, delete, and manage document collections
- **Conversation Memory**: Advanced memory management with automatic summarization
- **Modern UI**: React Ionic frontend with responsive design
- **REST API**: FastAPI backend with comprehensive API documentation
- **Secure Storage**: API key management
- **Vector Search**: ChromaDB for efficient document retrieval

## Architecture

The system implements a modular RAG architecture with separated frontend and backend:

1. **Frontend**: React Ionic application for user interface
2. **Backend**: FastAPI REST API for business logic
3. **Document Processing**: Upload and chunk documents using LlamaIndex
4. **Vector Storage**: Store embeddings in ChromaDB with HuggingFace BGE model
5. **Query Processing**: Retrieve relevant documents and generate responses
6. **Memory Management**: Track conversation history with intelligent summarization

## Project Structure

```
├── backend/                        # FastAPI backend
│   ├── src/                        # Core application logic
│   │   ├── rag/                    # RAG system components
│   │   │   ├── memory_manager.py   # Conversation memory
│   │   │   ├── rag_system.py       # Main RAG orchestrator
│   │   │   └── llm_query.py        # Multi-provider LLM interface
│   │   ├── app.py                  # Application functions
│   │   ├── chroma_setup.py         # ChromaDB initialization
│   │   ├── chroma_search.py        # Vector search operations
│   │   ├── config.py               # Configuration settings
│   │   └── api_keys.py             # API key management
│   ├── main.py                     # FastAPI application
│   ├── requirements.txt            # Python dependencies
│   └── README.md                   # Backend documentation
├── frontend/                       # React Ionic frontend
│   ├── src/
│   │   ├── components/             # React components
│   │   ├── pages/                  # Page components
│   │   ├── services/               # API service
│   │   └── types/                  # TypeScript types
│   ├── package.json                # Node dependencies
│   └── README.md                   # Frontend documentation
├── src/                            # Original source (legacy)
├── ui/                             # Original Streamlit UI (legacy)
├── chroma_db/                      # Vector database storage
└── docs/                           # Documentation
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Start the backend server**:
```bash
python main.py
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Install dependencies**:
```bash
cd frontend
npm install
```

2. **Start the development server**:
```bash
npm start
```

The app will open at `http://localhost:3000`

### Configuration

1. **Backend**: Configure settings in `backend/src/config.py`
2. **Frontend**: Update API URL in `frontend/.env` if needed

### Usage

1. Open the frontend at `http://localhost:3000`
2. Click on the "Settings" icon to configure your API keys
3. Select your preferred LLM provider (Groq, OpenAI, Gemini, or Deepseek)
4. Click on "Documents" to upload your documents
5. Start asking questions in the chat interface!

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check

### Documents
- `POST /api/documents/upload` - Upload a document
- `GET /api/documents` - List all documents
- `DELETE /api/documents/{doc_id}` - Delete a document
- `DELETE /api/documents/clear/all` - Clear all documents

### Chat
- `POST /api/chat/query` - Query the RAG system
- `POST /api/chat/clear` - Clear chat memory

### API Keys
- `POST /api/keys/save` - Save API key
- `GET /api/keys/{provider}` - Check if key exists
- `POST /api/keys/provider/set` - Set active provider
- `GET /api/keys/provider/get` - Get active provider

## Supported LLM Providers

- **Groq**: Fast inference with Llama models (Default)
- **OpenAI**: GPT-3.5-turbo and GPT-4 models
- **Google Gemini**: Gemini-Pro model
- **Deepseek**: Deepseek-chat model

## Technologies

### Backend
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Vector Database**: ChromaDB
- **Embeddings**: HuggingFace BGE-small-en-v1.5
- **LLM Integration**: Multiple provider APIs
- **Document Processing**: LlamaIndex

### Frontend
- **Framework**: React with TypeScript
- **UI Library**: Ionic React
- **HTTP Client**: Axios
- **Build Tool**: Create React App

## Development

### Backend Development

```bash
cd backend
# Install dependencies
pip install -r requirements.txt

# Run in development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
# Install dependencies
npm install

# Run development server
npm start

# Build for production
npm run build
```

## Production Deployment

### Backend
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend
```bash
cd frontend
npm run build
# Serve the build folder with a static server
```

## Docker Support

Docker support is available for the original Streamlit version. The new React/FastAPI stack can be containerized similarly.

## Security

- API keys are managed securely through the frontend
- Backend implements proper CORS configuration
- No sensitive data is logged or transmitted unnecessarily

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues, questions, or contributions, please open an issue on GitHub.
