```python
from llama_index.storage import SimpleVectorStore, SimpleDocumentStore
from llama_index import StorageContext

# Load all storage components
storage_context = StorageContext.from_defaults(
    docstore=SimpleDocumentStore.from_persist_dir(persist_dir),
    vector_store=SimpleVectorStore.from_persist_dir(persist_dir),
    index_store=SimpleIndexStore.from_persist_dir(persist_dir)
)

# Function to update document and its embedding
def update_document_and_embedding(doc_id, new_text, new_embedding):
    # Update document text
    storage_context.docstore.get_document(doc_id).text = new_text
    
    # Update embedding
    storage_context.vector_store.data[doc_id] = new_embedding
    
    # If you have an index, update it
    if hasattr(storage_context.vector_store, 'index'):
        storage_context.vector_store.index.update(doc_id, new_embedding)
    
    # Persist all changes
    storage_context.docstore.persist(persist_dir)
    storage_context.vector_store.persist(persist_dir)
    storage_context.index_store.persist(persist_dir)

# Usage
doc_id = "doc1"
new_text = "Updated document content"
new_embedding = [0.1, 0.2, 0.3, ...]  # Your new embedding
update_document_and_embedding(doc_id, new_text, new_embedding)
```