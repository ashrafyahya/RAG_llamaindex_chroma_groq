# ChromaDB: Complete Guide and Integration

## What is ChromaDB?

ChromaDB is an open-source vector database designed for AI applications. It provides a simple, fast, and scalable way to store and query embeddings, making it ideal for semantic search, recommendation systems, and other AI-powered features.

## How ChromaDB Works

### Core Architecture

ChromaDB operates on a client-server model with the following components:

1. **Client**: The interface that interacts with the database
2. **Server**: The backend that handles storage and retrieval
3. **Collections**: Containers that group related embeddings together
4. **Embeddings**: The high-dimensional vectors representing your data
5. **Metadata**: Additional information associated with each embedding

### Storage Options

ChromaDB offers two main storage modes:

1. **In-Memory**: Fast but temporary storage (data is lost when the application stops)
2. **Persistent**: Data is saved to disk and persists across sessions

### Indexing and Search

ChromaDB uses Hierarchical Navigable Small World (HNSW) indexing for efficient similarity search:

- HNSW creates a graph structure that enables fast approximate nearest neighbor search
- It balances search accuracy with computational efficiency
- Supports multiple distance metrics (cosine, euclidean, etc.)

## ChromaDB Functions and API

### 1. Client Initialization

```python
import chromadb

# In-memory client
client = chromadb.Client()

# Persistent client (data saved to disk)
client = chromadb.PersistentClient(path="../chroma_db")

# Remote client (connecting to a ChromaDB server)
client = chromadb.HttpClient(host="localhost", port=8000)
```

### 2. Collection Management

```python
# Create a new collection
collection = client.create_collection(name="my_collection")

# Get an existing collection
collection = client.get_collection(name="my_collection")

# Get or create a collection (returns existing if it exists)
collection = client.get_or_create_collection(name="my_collection")

# Delete a collection
client.delete_collection(name="my_collection")

# List all collections
collections = client.list_collections()
```

### 3. Adding Data

```python
# Add embeddings with IDs and metadata
collection.add(
    embeddings=[[1.1, 2.3, 3.2], [4.5, 6.9, 7.2]],  # List of embeddings
    ids=["doc1", "doc2"],                           # Unique identifiers
    metadatas=[{"source": "file1.txt"}, {"source": "file2.txt"}],  # Metadata
    documents=["This is document 1", "This is document 2"]        # Optional text content
)

# Add embeddings with automatic embedding generation
collection.add(
    ids=["doc3", "doc4"],
    documents=["Another document", "Yet another document"],
    metadatas=[{"source": "file3.txt"}, {"source": "file4.txt"}]
)
```

### 4. Querying Data

```python
# Query by embedding
results = collection.query(
    query_embeddings=[[1.1, 2.3, 3.2]],
    n_results=2  # Number of results to return
)

# Query by text (automatically generates embedding)
results = collection.query(
    query_texts=["Find similar documents to this text"],
    n_results=3
)

# Query with metadata filters
results = collection.query(
    query_texts=["Search query"],
    where={"source": {"$eq": "file1.txt"}},  # Filter by metadata
    n_results=5
)

# Complex metadata filters
results = collection.query(
    query_texts=["Search query"],
    where={
        "$and": [
            {"source": {"$ne": "file3.txt"}},  # Not equal to file3.txt
            {"metadata_field": {"$gt": 10}}    # Greater than 10
        ]
    },
    n_results=5
)
```

### 5. Retrieving Data

```python
# Get items by IDs
results = collection.get(ids=["doc1", "doc2"])

# Get items with metadata filters
results = collection.get(where={"source": {"$eq": "file1.txt"}})

# Get all items
results = collection.get()
```

### 6. Updating Data

```python
# Update embeddings
collection.update(
    ids=["doc1"],
    embeddings=[[1.1, 2.3, 3.3]],  # Updated embedding
    metadatas=[{"source": "file1_updated.txt"}]  # Updated metadata
)

# Update documents
collection.update(
    ids=["doc2"],
    documents=["Updated document content"]
)
```

### 7. Deleting Data

```python
# Delete by IDs
collection.delete(ids=["doc1", "doc2"])

# Delete with metadata filter
collection.delete(where={"source": {"$eq": "file1.txt"}})
```

### 8. Collection Information

```python
# Get collection count
count = collection.count()

# Get collection name and metadata
name = collection.name
metadata = collection.metadata
```

## Integrating ChromaDB with Your Workspace

### Step 1: Installation

```bash
pip install chromadb
```

### Step 2: Basic Setup

```python
# chroma_setup.py
import chromadb
import os

def setup_chroma(db_path="../chroma_db"):
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

if __name__ == "__main__":
    client, collection = setup_chroma()
    print(f"ChromaDB initialized with collection: {collection.name}")
```

### Step 3: Migrating Existing Embeddings

```python
# migrate_to_chroma.py
import json
import chromadb
from chroma_setup import setup_chroma
from typing import List, Dict, Any

def migrate_embeddings_to_chroma(embeddings_file: str, db_path: str = "../chroma_db"):
    """Migrate existing embeddings from JSON file to ChromaDB"""
    # Load existing embeddings
    with open(embeddings_file, 'r') as f:
        embeddings_data = json.load(f)

    # Setup ChromaDB
    client, collection = setup_chroma(db_path)

    # Prepare data for batch insertion
    ids = []
    embeddings = []
    metadatas = []
    documents = []

    for item in embeddings_data:
        ids.append(item["id"])
        embeddings.append(item["embedding"])

        # Create metadata dictionary
        metadata = {}
        if "source" in item:
            metadata["source"] = item["source"]
        # Add any other fields to metadata as needed
        metadatas.append(metadata)

        # Add document text if available
        if "text" in item:
            documents.append(item["text"])
        else:
            documents.append("")  # Empty string if no text

    # Insert in batches (recommended for large datasets)
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        end_idx = min(i + batch_size, len(ids))
        collection.add(
            ids=ids[i:end_idx],
            embeddings=embeddings[i:end_idx],
            metadatas=metadatas[i:end_idx],
            documents=documents[i:end_idx]
        )
        print(f"Added batch {i//batch_size + 1}: {end_idx-i} embeddings")

    print(f"Successfully migrated {len(ids)} embeddings to ChromaDB")
    return collection

if __name__ == "__main__":
    # Example usage
    embeddings_file = "embeddings.json"  # Your existing embeddings file
    db_path = "./chroma_db"

    collection = migrate_embeddings_to_chroma(embeddings_file, db_path)
    print(f"Migration complete. Collection now has {collection.count()} items")
```

### Step 4: Creating a Search Interface

```python
# chroma_search.py
import openai
import chromadb
from chroma_setup import setup_chroma
from typing import List, Dict, Any, Optional

class ChromaEmbeddingSearch:
    def __init__(self, db_path: str = "../chroma_db", collection_name: str = "document_embeddings"):
        """Initialize the ChromaDB search interface"""
        self.client, self.collection = setup_chroma(db_path)

        # Check if collection exists, create if not
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except:
            self.collection = self.client.create_collection(name=collection_name)

    def add_document(self, text: str, doc_id: str, metadata: Optional[Dict] = None):
        """Add a new document with automatic embedding generation"""
        # Generate embedding using OpenAI
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"
        )
        embedding = response["data"][0]["embedding"]

        # Add to collection
        self.collection.add(
            embeddings=[embedding],
            documents=[text],
            ids=[doc_id],
            metadatas=[metadata] if metadata else None
        )

        return f"Document {doc_id} added successfully"

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

# Example usage
if __name__ == "__main__":
    # Initialize search interface
    search = ChromaEmbeddingSearch()

    # Add a new document
    result = search.add_document(
        text="This is a sample document about machine learning",
        doc_id="doc_001",
        metadata={"source": "example.txt", "category": "AI"}
    )
    print(result)

    # Search for similar documents
    results = search.search_by_text("deep learning algorithms", n_results=3)

    # Display results
    print("
Search Results:")
    for i, (doc_id, document, metadata, distance) in enumerate(zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    )):
        print(f"
Result {i+1}:")
        print(f"Document ID: {doc_id}")
        print(f"Similarity: {1-distance:.4f}")
        print(f"Document: {document[:100]}...")
        print(f"Metadata: {metadata}")
```

### Step 5: Building a Streamlit Interface

```python
# chroma_streamlit_app.py
import streamlit as st
import openai
from chroma_search import ChromaEmbeddingSearch
import time

def main():
    st.title("Document Search with ChromaDB")

    # Initialize session state
    if 'search' not in st.session_state:
        st.session_state.search = ChromaEmbeddingSearch()

    search = st.session_state.search

    # Sidebar for configuration
    st.sidebar.header("Configuration")
    db_path = st.sidebar.text_input("Database Path", "./chroma_db")
    n_results = st.sidebar.slider("Number of Results", min_value=1, max_value=20, value=5)

    # Main interface tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Search", "Add Document", "Update Document", "Manage"])

    # Search tab
    with tab1:
        st.header("Search Documents")
        query = st.text_input("Enter your search query:")

        # Advanced filter options
        with st.expander("Advanced Filters"):
            filter_key = st.text_input("Metadata Filter Key:")
            filter_value = st.text_input("Metadata Filter Value:")
            use_filter = st.checkbox("Apply Filter")

        if st.button("Search"):
            if query:
                with st.spinner("Searching..."):
                    # Prepare filter if specified
                    metadata_filter = None
                    if use_filter and filter_key and filter_value:
                        metadata_filter = {filter_key: {"$eq": filter_value}}

                    # Perform search
                    results = search.search_by_text(query, n_results, metadata_filter)

                # Display results
                st.subheader("Search Results")
                if results["ids"][0]:
                    for i, (doc_id, document, metadata, distance) in enumerate(zip(
                        results["ids"][0],
                        results["documents"][0],
                        results["metadatas"][0],
                        results["distances"][0]
                    )):
                        with st.expander(f"Result {i+1} - Similarity: {1-distance:.4f}"):
                            st.write(f"**Document ID:** {doc_id}")
                            st.write(f"**Similarity:** {1-distance:.4f}")
                            st.write(f"**Document:** {document}")
                            st.write(f"**Metadata:** {metadata}")
                else:
                    st.info("No results found")

    # Add document tab
    with tab2:
        st.header("Add New Document")
        doc_text = st.text_area("Document Text:", height=200)
        doc_id = st.text_input("Document ID:")

        # Metadata fields
        with st.expander("Metadata"):
            metadata = {}
            source = st.text_input("Source:")
            category = st.text_input("Category:")
            if source:
                metadata["source"] = source
            if category:
                metadata["category"] = category

        if st.button("Add Document"):
            if doc_text and doc_id:
                with st.spinner("Adding document..."):
                    result = search.add_document(doc_text, doc_id, metadata if metadata else None)
                st.success(result)
                time.sleep(1)  # Give time for the database to update
                st.rerun()
            else:
                st.error("Please provide both document text and ID")

    # Update document tab
    with tab3:
        st.header("Update Document")
        update_id = st.text_input("Document ID to Update:")

        # Check if document exists
        if update_id:
            doc = search.get_document_by_id(update_id)
            if doc["ids"]:
                # Display current document
                with st.expander("Current Document"):
                    st.write(f"**ID:** {doc['ids'][0]}")
                    st.write(f"**Text:** {doc['documents'][0] if doc['documents'] else 'No text'}")
                    st.write(f"**Metadata:** {doc['metadatas'][0] if doc['metadatas'] else 'No metadata'}")

                # Update form
                new_text = st.text_area("New Document Text:", value=doc['documents'][0] if doc['documents'] else "", height=200)

                with st.expander("Update Metadata"):
                    new_metadata = {}
                    if doc['metadatas'] and doc['metadatas'][0]:
                        # Display current metadata
                        for key, value in doc['metadatas'][0].items():
                            new_value = st.text_input(f"{key}:", value=value)
                            if new_value:
                                new_metadata[key] = new_value

                    # Add new metadata fields
                    new_key = st.text_input("New Metadata Key:")
                    new_value = st.text_input("New Metadata Value:")
                    if new_key and new_value:
                        new_metadata[new_key] = new_value

                if st.button("Update Document"):
                    with st.spinner("Updating document..."):
                        result = search.update_document(update_id, new_text, new_metadata if new_metadata else None)
                    st.success(result)
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("Document not found")

    # Manage tab
    with tab4:
        st.header("Manage Documents")

        # List documents with pagination
        limit = st.slider("Documents per page:", min_value=5, max_value=50, value=10)
        documents = search.list_all_documents(limit=limit)

        if documents["ids"]:
            st.write(f"Showing {len(documents['ids'])} documents:")

            for i, (doc_id, document, metadata) in enumerate(zip(
                documents["ids"],
                documents["documents"] if documents["documents"] else [""] * len(documents["ids"]),
                documents["metadatas"] if documents["metadatas"] : [{}] * len(documents["ids"])
            )):
                with st.expander(f"Document: {doc_id}"):
                    st.write(f"**ID:** {doc_id}")
                    st.write(f"**Text:** {document[:100]}...")
                    st.write(f"**Metadata:** {metadata}")

                    # Delete button
                    if st.button(f"Delete {doc_id}", key=f"del_{i}"):
                        with st.spinner("Deleting document..."):
                            result = search.delete_document(doc_id)
                        st.success(result)
                        time.sleep(1)
                        st.rerun()
        else:
            st.info("No documents in the database")

if __name__ == "__main__":
    main()
```

## Advanced ChromaDB Features

### 1. Custom Embedding Functions

```python
# custom_embedding.py
import chromadb
from chromadb.utils import embedding_functions

# Use a custom embedding function
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.Client()
collection = client.create_collection(
    name="my_collection",
    embedding_function=ef  # Use custom embedding function
)

# Now you can add text directly without providing embeddings
collection.add(
    ids=["doc1", "doc2"],
    documents=["This is a document", "This is another document"]
)
```

### 2. Working with Different Distance Metrics

```python
# Create collection with specific distance metric
collection = client.create_collection(
    name="my_collection",
    metadata={"hnsw:space": "l2"}  # Options: "l2", "ip", "cosine"
)
```

### 3. Server Mode

```python
# Start ChromaDB server (in terminal)
chroma run --host localhost --port 8000

# Connect to server in Python
client = chromadb.HttpClient(host='localhost', port=8000)
```

## Best Practices

1. **Batch Operations**: Insert and update data in batches for better performance
2. **Metadata Design**: Structure metadata to enable efficient filtering
3. **ID Management**: Use consistent and meaningful IDs for your documents
4. **Resource Management**: Monitor memory usage, especially with large collections
5. **Backups**: Regularly back up your ChromaDB data directory

## Troubleshooting

1. **Memory Issues**: Reduce batch size or use server mode for large datasets
2. **Slow Queries**: Check index parameters and consider rebuilding indexes
3. **Connection Problems**: Ensure the ChromaDB server is running and accessible
4. **Data Corruption**: Restore from backups if data becomes corrupted

This guide should provide you with everything you need to effectively integrate ChromaDB into your workspace, from basic setup to advanced features and best practices.
