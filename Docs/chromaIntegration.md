# Integrating ChromaDB with app.py

## Setting Up ChromaDB in Your Application

This guide shows you how to integrate ChromaDB directly into your app.py file and load embeddings into it.

### Step 1: Modify app.py to Include ChromaDB

First, let's modify your app.py to initialize ChromaDB when the application starts:

```python
# app.py
import os
import json
import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np

# Initialize session state for ChromaDB
if 'chroma_client' not in st.session_state:
    # Create persistent client (data will be saved to disk)
    st.session_state.chroma_client = chromadb.PersistentClient(path="./chroma_db")

    # Get or create collection
    st.session_state.collection = st.session_state.chroma_client.get_or_create_collection(
        name="document_embeddings",
        metadata={"hnsw:space": "cosine"}  # Using cosine similarity
    )

# Initialize sentence transformer model
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_embedding_model()

# Function to load embeddings into ChromaDB
def load_embeddings_to_chroma(embeddings_file):
    """Load embeddings from JSON file into ChromaDB"""
    # Check if collection already has data
    if st.session_state.collection.count() > 0:
        st.warning("Collection already contains data. Skipping loading.")
        return

    # Load embeddings from file
    with open(embeddings_file, 'r') as f:
        embeddings_data = json.load(f)

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
        st.session_state.collection.add(
            ids=ids[i:end_idx],
            embeddings=embeddings[i:end_idx],
            metadatas=metadatas[i:end_idx],
            documents=documents[i:end_idx]
        )

    st.success(f"Successfully loaded {len(ids)} embeddings into ChromaDB")

# Function to search ChromaDB
def search_chroma(query_text, n_results=5):
    """Search ChromaDB with a text query"""
    # Generate embedding for the query
    query_embedding = model.encode(query_text).tolist()

    # Search the collection
    results = st.session_state.collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results

# Main application
def main():
    st.title("Document Search with ChromaDB")

    # Sidebar for loading embeddings
    with st.sidebar:
        st.header("Embeddings Management")
        embeddings_file = st.file_uploader("Upload embeddings JSON file", type=["json"])

        if embeddings_file is not None:
            # Save uploaded file
            with open("uploaded_embeddings.json", "wb") as f:
                f.write(embeddings_file.getbuffer())

            # Load embeddings into ChromaDB
            if st.button("Load Embeddings"):
                with st.spinner("Loading embeddings..."):
                    load_embeddings_to_chroma("uploaded_embeddings.json")

    # Display collection info
    st.sidebar.subheader("Collection Info")
    st.sidebar.write(f"Document count: {st.session_state.collection.count()}")

    # Search interface
    st.header("Search Documents")
    query_text = st.text_input("Enter your search query:")
    n_results = st.slider("Number of results", min_value=1, max_value=20, value=5)

    if st.button("Search") and query_text:
        with st.spinner("Searching..."):
            results = search_chroma(query_text, n_results)

            # Display results
            if results["ids"][0]:
                st.subheader("Search Results")
                for i, (doc_id, metadata, document, distance) in enumerate(zip(
                    results["ids"][0], 
                    results["metadatas"][0], 
                    results["documents"][0],
                    results["distances"][0]
                )):
                    with st.expander(f"Result {i+1}: {doc_id} (Similarity: {1-distance:.4f})"):
                        st.write(f"**Document ID:** {doc_id}")
                        if metadata and "source" in metadata:
                            st.write(f"**Source:** {metadata['source']}")
                        st.write(f"**Content:** {document}")
            else:
                st.warning("No results found")

if __name__ == "__main__":
    main()
```

### Step 2: Creating a Script to Generate Embeddings

If you need to generate embeddings from your documents first, here's a helper script:

```python
# generate_embeddings.py
import os
import json
from sentence_transformers import SentenceTransformer
import glob

def generate_embeddings_from_documents(docs_dir="documents", output_file="embeddings.json"):
    """Generate embeddings from text documents and save to JSON"""
    # Initialize model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Find all text files
    file_paths = glob.glob(os.path.join(docs_dir, "*.txt"))

    embeddings_data = []

    for file_path in file_paths:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        # Generate embedding
        embedding = model.encode(text).tolist()

        # Create record
        record = {
            "id": os.path.basename(file_path),
            "source": file_path,
            "text": text,
            "embedding": embedding
        }

        embeddings_data.append(record)
        print(f"Processed {file_path}")

    # Save to JSON
    with open(output_file, 'w') as f:
        json.dump(embeddings_data, f)

    print(f"Saved {len(embeddings_data)} embeddings to {output_file}")

if __name__ == "__main__":
    generate_embeddings_from_documents()
```

### Step 3: Creating a Script to Load Existing Embeddings

If you already have embeddings in another format, you can use this script to load them into ChromaDB:

```python
# load_embeddings_to_chroma.py
import json
import chromadb
import os

def load_embeddings_to_chroma(embeddings_file, db_path="./chroma_db"):
    """Load embeddings from JSON file into ChromaDB"""
    # Create directory if it doesn't exist
    os.makedirs(db_path, exist_ok=True)

    # Initialize persistent client
    client = chromadb.PersistentClient(path=db_path)

    # Get or create collection
    collection = client.get_or_create_collection(
        name="document_embeddings",
        metadata={"hnsw:space": "cosine"}
    )

    # Load embeddings from file
    with open(embeddings_file, 'r') as f:
        embeddings_data = json.load(f)

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

    print(f"Successfully loaded {len(ids)} embeddings to ChromaDB")
    return collection

if __name__ == "__main__":
    # Example usage
    embeddings_file = "embeddings.json"  # Your embeddings file
    db_path = "./chroma_db"

    collection = load_embeddings_to_chroma(embeddings_file, db_path)
    print(f"Collection now has {collection.count()} items")
```

### Step 4: Running the Application

1. First, generate embeddings if needed:
   ```bash
   python generate_embeddings.py
   ```

2. Or load existing embeddings into ChromaDB:
   ```bash
   python load_embeddings_to_chroma.py
   ```

3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

### Step 5: Using the App

1. The app will initialize ChromaDB when it starts
2. You can upload an embeddings JSON file through the sidebar
3. Click "Load Embeddings" to populate the database
4. Use the search interface to query your documents

### Advanced Features

#### Adding New Documents Directly

```python
# Add this function to app.py
def add_document_to_chroma(text, doc_id=None, metadata=None):
    """Add a new document directly to ChromaDB"""
    # Generate embedding
    embedding = model.encode(text).tolist()

    # Generate ID if not provided
    if doc_id is None:
        doc_id = f"doc_{st.session_state.collection.count() + 1}"

    # Add to collection
    st.session_state.collection.add(
        embeddings=[embedding],
        documents=[text],
        ids=[doc_id],
        metadatas=[metadata] if metadata else None
    )

    return doc_id
```

#### Updating Documents

```python
# Add this function to app.py
def update_document_in_chroma(doc_id, new_text=None, new_metadata=None):
    """Update an existing document in ChromaDB"""
    update_args = {"ids": [doc_id]}

    if new_text:
        # Generate new embedding
        embedding = model.encode(new_text).tolist()
        update_args["embeddings"] = [embedding]
        update_args["documents"] = [new_text]

    if new_metadata:
        update_args["metadatas"] = [new_metadata]

    st.session_state.collection.update(**update_args)
    return f"Document {doc_id} updated"
```

#### Deleting Documents

```python
# Add this function to app.py
def delete_document_from_chroma(doc_id):
    """Delete a document from ChromaDB"""
    st.session_state.collection.delete(ids=[doc_id])
    return f"Document {doc_id} deleted"
```

### Best Practices

1. **Batch Processing**: Always add/update/delete in batches for better performance
2. **Error Handling**: Add proper error handling for file operations
3. **Progress Indicators**: Use Streamlit's progress indicators for long operations
4. **Caching**: Cache frequently accessed data to improve performance
5. **Data Validation**: Validate embeddings before adding to the database

This integration allows you to use ChromaDB seamlessly within your Streamlit application, providing efficient storage and retrieval of document embeddings.
