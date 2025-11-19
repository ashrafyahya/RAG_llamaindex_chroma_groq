# RAG System Backend API

FastAPI-based REST API for the RAG (Retrieval-Augmented Generation) system.

## Features

- **Document Management**: Upload, list, delete documents
- **RAG Query System**: Query documents with multiple LLM providers
- **API Key Management**: Secure storage and retrieval of API keys
- **Multiple LLM Providers**: Support for Groq, OpenAI, Gemini, and Deepseek
- **Chat Memory**: Conversation history management

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Running the Server

### Development Mode
```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

### Production Mode with Uvicorn
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check

### Document Management
- `POST /api/documents/upload` - Upload a document
- `GET /api/documents` - List all documents
- `DELETE /api/documents/{doc_id}` - Delete a document
- `DELETE /api/documents/clear/all` - Clear all documents

### Chat/Query
- `POST /api/chat/query` - Query the RAG system
- `POST /api/chat/clear` - Clear chat memory

### API Key Management
- `POST /api/keys/save` - Save API key for a provider
- `GET /api/keys/{provider}` - Check if provider has API key
- `POST /api/keys/provider/set` - Set active provider
- `GET /api/keys/provider/get` - Get active provider

## Example Usage

### Upload a Document
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

### Query the System
```bash
curl -X POST "http://localhost:8000/api/chat/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic of the document?",
    "api_provider": "groq",
    "api_key_groq": "your-api-key"
  }'
```

### List Documents
```bash
curl -X GET "http://localhost:8000/api/documents"
```

## Configuration

The backend uses the same configuration from `src/config.py`:
- `MODEL_NAME`: Default LLM model
- `TOKEN_LIMIT`: Maximum tokens per request
- `SUMMARIZE_THRESHOLD`: Memory management threshold

## Dependencies

- FastAPI: Web framework
- Uvicorn: ASGI server
- LlamaIndex: RAG framework
- ChromaDB: Vector database
- Multiple LLM providers (Groq, OpenAI, Gemini, Deepseek)

## CORS Configuration

By default, CORS is configured to allow all origins for development. For production, update the `allow_origins` in `main.py` to specific domains.

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request
- `404`: Not found
- `500`: Internal server error

Error responses include a `detail` field with the error message.
