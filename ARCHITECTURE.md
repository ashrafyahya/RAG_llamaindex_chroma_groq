# RAG System Architecture

## Overview

The RAG system has been migrated from a monolithic Streamlit application to a modern, scalable architecture with separated frontend and backend.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAG SYSTEM                               │
└─────────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┴─────────────────┐
            │                                   │
            ▼                                   ▼
┌──────────────────────┐              ┌──────────────────────┐
│     FRONTEND         │              │      BACKEND         │
│   React Ionic        │◄────REST────►│     FastAPI          │
│   TypeScript         │     API      │      Python          │
│   Port: 3000         │              │    Port: 8000        │
└──────────────────────┘              └──────────────────────┘
            │                                   │
            │                                   │
            ▼                                   ▼
┌──────────────────────┐              ┌──────────────────────┐
│   UI Components      │              │   RAG System         │
├──────────────────────┤              ├──────────────────────┤
│ • ChatInterface      │              │ • Document Manager   │
│ • DocumentMgmt       │              │ • Vector Search      │
│ • APISettings        │              │ • LLM Query          │
└──────────────────────┘              │ • Memory Manager     │
                                      └──────────────────────┘
                                                │
                                                ▼
                                      ┌──────────────────────┐
                                      │   External Services  │
                                      ├──────────────────────┤
                                      │ • ChromaDB           │
                                      │ • HuggingFace        │
                                      │ • LLM Providers:     │
                                      │   - Groq             │
                                      │   - OpenAI           │
                                      │   - Gemini           │
                                      │   - Deepseek         │
                                      └──────────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **UI Library**: Ionic React
- **HTTP Client**: Axios
- **State Management**: React Hooks (useState, useEffect)
- **Styling**: Ionic CSS + Custom CSS
- **Build Tool**: Create React App

### Backend
- **Framework**: FastAPI
- **Server**: Uvicorn (ASGI)
- **Vector Database**: ChromaDB
- **Embeddings**: HuggingFace (BGE-small-en-v1.5)
- **Document Processing**: LlamaIndex
- **LLM Integration**: Multiple providers
- **Language**: Python 3.8+

## API Endpoints

### Health & Info
- `GET /` - Root endpoint
- `GET /health` - Health check

### Documents
- `POST /api/documents/upload` - Upload document
- `GET /api/documents` - List all documents
- `DELETE /api/documents/{id}` - Delete document
- `DELETE /api/documents/clear/all` - Clear all documents

### Chat
- `POST /api/chat/query` - Query RAG system
- `POST /api/chat/clear` - Clear chat history

### API Keys
- `POST /api/keys/save` - Save API key
- `GET /api/keys/{provider}` - Check key existence
- `POST /api/keys/provider/set` - Set active provider
- `GET /api/keys/provider/get` - Get active provider

## Data Flow

### Document Upload Flow
```
User → Frontend Upload Component → API Service → Backend /api/documents/upload
                                                          ↓
                                                   LlamaIndex Process
                                                          ↓
                                                   Generate Embeddings
                                                          ↓
                                                   Store in ChromaDB
```

### Query Flow
```
User Query → Frontend Chat → API Service → Backend /api/chat/query
                                                    ↓
                                              Search ChromaDB
                                                    ↓
                                              Retrieve Documents
                                                    ↓
                                              Format Context
                                                    ↓
                                              LLM API Call
                                                    ↓
                                              Return Response
```

## Security Considerations

1. **API Keys**: Stored in memory during session, not persisted by default
2. **CORS**: Configured to allow frontend origin
3. **Input Validation**: Pydantic models validate API requests
4. **File Upload**: Only specific file types allowed (txt, pdf, docx, md)

## Deployment Options

### Development
- **Backend**: `python backend/main.py`
- **Frontend**: `npm start` in frontend/
- **Combined**: `./start.sh` or `start.bat`

### Production
- **Backend**: Uvicorn with workers (`uvicorn main:app --workers 4`)
- **Frontend**: Build and serve static files (`npm run build`)
- **Reverse Proxy**: Nginx to serve both services
- **Docker**: Can be containerized separately or together

## Directory Structure

```
RAG_llamaindex_chroma_groq/
├── backend/                    # Backend application
│   ├── src/                    # Source code
│   │   ├── rag/               # RAG system modules
│   │   ├── app.py             # Application logic
│   │   ├── api_keys.py        # API key management
│   │   ├── chroma_*.py        # ChromaDB operations
│   │   └── config.py          # Configuration
│   ├── main.py                # FastAPI entry point
│   ├── requirements.txt       # Python dependencies
│   └── README.md              # Backend documentation
│
├── frontend/                   # Frontend application
│   ├── src/                   # Source code
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API service
│   │   └── types/             # TypeScript types
│   ├── public/                # Static assets
│   ├── package.json           # Node dependencies
│   └── README.md              # Frontend documentation
│
├── docs/                      # Documentation
├── README.md                  # Main documentation
├── start.sh                   # Linux/Mac startup script
└── start.bat                  # Windows startup script
```

## Key Benefits of New Architecture

1. **Separation of Concerns**: Frontend and backend are independent
2. **Scalability**: Can scale frontend and backend separately
3. **Technology Flexibility**: Can replace frontend or backend without affecting the other
4. **API-First**: REST API can be consumed by mobile apps, CLI tools, etc.
5. **Modern UI**: Ionic provides native-like experience on web and mobile
6. **Type Safety**: TypeScript in frontend reduces bugs
7. **Maintainability**: Clear structure makes maintenance easier
8. **Testing**: Can test frontend and backend independently

## Migration Notes

### Changes from Streamlit Version
- ✅ Removed Streamlit dependency
- ✅ Added FastAPI REST API
- ✅ Created React Ionic frontend
- ✅ Improved component structure
- ✅ Better state management
- ✅ Enhanced API documentation
- ✅ Separated frontend/backend concerns

### Preserved Functionality
- ✅ Document upload and management
- ✅ Chat with RAG system
- ✅ Multiple LLM provider support
- ✅ API key management
- ✅ Conversation memory
- ✅ Vector search with ChromaDB

## Future Enhancements

1. **Authentication**: Add user authentication and authorization
2. **Database**: Persistent storage for chat history
3. **Real-time**: WebSocket support for streaming responses
4. **Mobile**: Build native iOS/Android apps with Ionic Capacitor
5. **Docker**: Complete Docker Compose setup
6. **CI/CD**: Automated testing and deployment
7. **Monitoring**: Add logging and monitoring tools
8. **PDF Export**: Restore PDF export for chat history
