import openai
import chromadb
from chroma_setup import setup_chroma
from typing import List, Dict, Any, Optional

# src/chroma_search.py
class ChromaEmbeddingSearch:
    def __init__(self, db_path: str = "..\\chroma_db", collection_name: str = "document_embeddings"):
        """Initialize the ChromaDB search interface"""
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
    def add_document(self, text: str, doc_id: str, metadata: Optional[Dict] = None):
        """Add a new document with automatic embedding generation"""
        self.collection.add(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata] if metadata else None
        )


    def search_by_text(self, query_text: str, n_results: int = 5, 
                      metadata_filter: Optional[Dict] = None) -> Dict:
        """Search for similar documents using text query"""
        # Prepare query arguments
        query_args = {
            "query_texts": [query_text],
            "n_results": n_results
        }

        # Add metadata filter if provided
        if metadata_filter:
            query_args["where"] = metadata_filter

        # Execute query
        results = self.collection.query(**query_args)

        return results

    def search_by_embedding(self, query_embedding: List[float], n_results: int = 5,
                          metadata_filter: Optional[Dict] = None) -> Dict:
        """Search for similar documents using embedding vector"""
        # Prepare query arguments
        query_args = {
            "query_embeddings": [query_embedding],
            "n_results": n_results
        }

        # Add metadata filter if provided
        if metadata_filter:
            query_args["where"] = metadata_filter

        # Execute query
        results = self.collection.query(**query_args)

        return results

    def get_document_by_id(self, doc_id: str) -> Dict:
        """Retrieve a specific document by ID"""
        return self.collection.get(ids=[doc_id])

    def update_document(self, doc_id: str, text: Optional[str] = None, 
                       metadata: Optional[Dict] = None):
        """Update an existing document"""
        update_args = {"ids": [doc_id]}

        if text:
            # Generate new embedding
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            embedding = response["data"][0]["embedding"]

            update_args["embeddings"] = [embedding]
            update_args["documents"] = [text]

        if metadata:
            update_args["metadatas"] = [metadata]

        self.collection.update(**update_args)
        return f"Document {doc_id} updated successfully"

    def delete_document(self, doc_id: str):
        """Delete a document by ID"""
        self.collection.delete(ids=[doc_id])
        return f"Document {doc_id} deleted successfully"

    def list_all_documents(self, limit: Optional[int] = None) -> Dict:
        """List all documents in the collection"""
        get_args = {}
        if limit:
            get_args["limit"] = limit

        return self.collection.get(**get_args)
