"""
Main Application Module
Orchestrates RAG system and query processing
"""
from typing import Optional
from dotenv import load_dotenv

from src.rag.llm_query import process_query
from src.rag.rag_system import get_rag_system

load_dotenv()

# Initialize RAG system
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
    """Query ChromaDB and generate response with LLM"""
    # Search for relevant documents
    results = rag_system.search_documents(query, n_results)
    
    # Check similarity threshold
    similarities = results.get("distances", [[]])[0]
    if similarities:
        print(f"min(similarities): {min(similarities)}")
    
    if not similarities or min(similarities) < 0.70:
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


def chat_with_rag():
    """Interactive chat loop"""
    while True:
        query = input("\nEnter your query (or 'quit' to exit): ")
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        response = query_documents(query)
        print("\nResponse:\n", response)


if __name__ == "__main__":
    # load_documents()
    chat_with_rag()
