import chromadb
import os

def setup_chroma(db_path="..\\chroma_db"):
    """Initialize ChromaDB with a persistent storage"""
    # Create directory if it doesn't exist
    os.makedirs(db_path, exist_ok=True)

    # Initialize persistent client
    client = chromadb.PersistentClient(path=db_path)

    # Get or create collection
    collection = client.get_or_create_collection(
        name="document_embeddings",
        metadata={"hnsw:space": "cosine"}  # Using cosine similarity
    )

    return client, collection
