"""
FastAPI Backend for RAG System
Main application entry point
"""
import os
import sys
from typing import Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Add backend/src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import (
    clear_all_documents,
    clear_chat_memory,
    delete_document,
    get_uploaded_documents,
    query_documents,
    upload_document,
)
from src.api_keys import APIKeyManager

# Initialize FastAPI app
app = FastAPI(
    title="RAG System API",
    description="REST API for RAG-based AI Assistant with document management and chat capabilities",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Manager instance
api_key_manager = APIKeyManager()


# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    n_results: int = 3
    api_provider: str = "groq"
    api_key_groq: Optional[str] = None
    api_key_openai: Optional[str] = None
    api_key_gemini: Optional[str] = None
    api_key_deepseek: Optional[str] = None


class QueryResponse(BaseModel):
    response: str
    success: bool


class DocumentResponse(BaseModel):
    message: str
    success: bool


class APIKeyRequest(BaseModel):
    provider: str
    api_key: str


class APIKeyResponse(BaseModel):
    message: str
    success: bool


class ProviderRequest(BaseModel):
    provider: str


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {"message": "RAG System API is running", "status": "healthy"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "rag-api"}


# Document management endpoints
@app.post("/api/documents/upload", response_model=DocumentResponse)
async def upload_document_endpoint(file: UploadFile = File(...)):
    """
    Upload a document to the RAG system
    
    Args:
        file: Document file (txt, pdf, docx, md)
    
    Returns:
        DocumentResponse with success status and message
    """
    try:
        result = upload_document(file)
        success = "Successfully" in result
        return DocumentResponse(message=result, success=success)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents", response_model=List[Dict])
async def list_documents():
    """
    Get list of all uploaded documents
    
    Returns:
        List of documents with metadata
    """
    try:
        documents = get_uploaded_documents()
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/documents/{doc_id}", response_model=DocumentResponse)
async def delete_document_endpoint(doc_id: str):
    """
    Delete a specific document by ID
    
    Args:
        doc_id: Document identifier
    
    Returns:
        DocumentResponse with success status and message
    """
    try:
        result = delete_document(doc_id)
        success = "successfully" in result.lower()
        return DocumentResponse(message=result, success=success)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/documents/clear/all", response_model=DocumentResponse)
async def clear_all_documents_endpoint():
    """
    Clear all documents from the database
    
    Returns:
        DocumentResponse with success status and message
    """
    try:
        result = clear_all_documents()
        success = "Successfully" in result
        return DocumentResponse(message=result, success=success)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Chat endpoints
@app.post("/api/chat/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Query the RAG system with a question
    
    Args:
        request: QueryRequest with query text and API configuration
    
    Returns:
        QueryResponse with generated answer
    """
    try:
        response = query_documents(
            query=request.query,
            n_results=request.n_results,
            api_provider=request.api_provider,
            api_key_groq=request.api_key_groq,
            api_key_openai=request.api_key_openai,
            api_key_gemini=request.api_key_gemini,
            api_key_deepseek=request.api_key_deepseek,
        )
        return QueryResponse(response=response, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/clear", response_model=DocumentResponse)
async def clear_chat_endpoint():
    """
    Clear chat memory/history
    
    Returns:
        DocumentResponse with success status
    """
    try:
        clear_chat_memory()
        return DocumentResponse(message="Chat memory cleared successfully", success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# API Key management endpoints
@app.post("/api/keys/save", response_model=APIKeyResponse)
async def save_api_key(request: APIKeyRequest):
    """
    Save an API key for a specific provider
    
    Args:
        request: APIKeyRequest with provider and key
    
    Returns:
        APIKeyResponse with success status
    """
    try:
        api_key_manager.save_api_key(request.provider, request.api_key)
        return APIKeyResponse(
            message=f"API key for {request.provider} saved successfully",
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/keys/{provider}")
async def get_api_key(provider: str):
    """
    Retrieve API key for a specific provider
    
    Args:
        provider: Provider name (groq, openai, gemini, deepseek)
    
    Returns:
        API key or empty string
    """
    try:
        key = api_key_manager.get_api_key(provider)
        return {"provider": provider, "has_key": bool(key)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/keys/provider/set", response_model=APIKeyResponse)
async def set_selected_provider(request: ProviderRequest):
    """
    Set the active LLM provider
    
    Args:
        request: ProviderRequest with provider name
    
    Returns:
        APIKeyResponse with success status
    """
    try:
        api_key_manager.save_selected_provider(request.provider)
        return APIKeyResponse(
            message=f"Active provider set to {request.provider}",
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/keys/provider/get")
async def get_selected_provider():
    """
    Get the currently active LLM provider
    
    Returns:
        Current provider name
    """
    try:
        provider = api_key_manager.get_selected_provider()
        return {"provider": provider}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
