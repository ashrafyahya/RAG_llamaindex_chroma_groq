"""
Chroma Database Setup Module
Provides utilities for initializing and configuring ChromaDB persistent storage
"""
import os

import chromadb


def setup_chroma(db_path="..\\chroma_db"):
    """
    Initialize ChromaDB with persistent storage for document embeddings.
    
    Args:
        db_path (str): Path to the directory where ChromaDB files will be stored.
                      Defaults to "..\\chroma_db" relative to current directory.
    
    Returns:
        tuple: A tuple containing (client, collection) where:
            - client: ChromaDB PersistentClient instance
            - collection: ChromaDB collection for document embeddings
    
    Note:
        The collection uses cosine similarity for vector comparisons.
    """
    os.makedirs(db_path, exist_ok=True)

    # Initialize persistent client
    client = chromadb.PersistentClient(path=db_path)

    # Get or create collection
    collection = client.get_or_create_collection(
        name="document_embeddings",
        metadata={"hnsw:space": "cosine"}
    )

    return client, collection
