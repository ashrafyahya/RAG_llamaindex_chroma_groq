"""
Main Application Module
Orchestrates RAG system and query processing
"""
from typing import Optional

from src.rag import memory_manager
from src.rag.llm_query import process_query
from src.rag.rag_system import get_rag_system

# Initialize the global RAG system instance
rag_system = get_rag_system()


def load_documents():
    """Load documents from the data directory"""
    rag_system.load_documents()


def query_documents(
    query: str,
    n_results: int = 3,
    api_provider: str = "groq",
    api_key_groq: Optional[str] = None,
    api_key_openai: Optional[str] = None,
    api_key_gemini: Optional[str] = None,
    api_key_deepseek: Optional[str] = None
):
    """
    Query the document database and generate a response using the selected LLM.
    
    Args:
        query (str): The user's question
        n_results (int): Number of similar documents to retrieve
        api_provider (str): LLM provider to use (groq, openai, gemini, deepseek)
        api_key_* (Optional[str]): API keys for respective providers
        
    Returns:
        str: Generated response from the LLM based on retrieved documents
    """
    results = rag_system.search_documents(query, n_results)
    
    # Check document distance scores (lower distance = more similar)
    distances = results.get("distances", [[]])[0]
    if distances:
        print(f"Best distance score: {min(distances):.4f} (lower = more similar)")
    
    # Filter out results if distance is too high (less similar)
    if not distances or min(distances) > 0.7:
        return "I don't have enough information to answer this question."
    
    # Format context from search results
    context = rag_system.format_search_results(results, query)
    
    # Process query with LLM
    answer = process_query(
        query,
        context,
        api_provider=api_provider,
        api_key_groq=api_key_groq,
        api_key_openai=api_key_openai,
        api_key_gemini=api_key_gemini,
        api_key_deepseek=api_key_deepseek
    )
    
    return answer


def upload_document(uploaded_file):
    """Upload and index a document"""
    return rag_system.upload_document(uploaded_file)


def delete_document(doc_id: str):
    """Delete a document"""
    return rag_system.delete_document(doc_id)


def get_uploaded_documents():
    """Get list of uploaded documents"""
    return rag_system.get_uploaded_documents()


def clear_all_documents():
    """Clear all documents from database"""
    return rag_system.clear_all_documents()


def clear_chat_memory():
    """
    Clear the conversation memory by resetting the chat history.
    This allows users to start fresh conversations without context.
    """
    memory_manager.chat_history = []


def chat_with_rag():
    """
    Start an interactive command-line chat session with the RAG system.
    Users can ask questions and receive responses based on loaded documents.
    Type 'quit', 'exit', or 'q' to end the session.
    """
    while True:
        query = input("\nEnter your query (or 'quit' to exit): ")
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        response = query_documents(query)
        print("\nResponse:\n", response)


if __name__ == "__main__":
    chat_with_rag()
