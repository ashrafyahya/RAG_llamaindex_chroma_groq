```python
from llama_index import StorageContext
from llama_index.storage import SimpleVectorStore, SimpleDocumentStore, SimpleIndexStore

def delete_document_and_embedding(doc_id, persist_dir):
    """
    Delete a document and its related embedding and index entries.
    
    Args:
        doc_id: The ID of the document to delete
        persist_dir: Directory where storage is persisted
    """
    # Load storage context
    storage_context = StorageContext.from_defaults(
        docstore=SimpleDocumentStore.from_persist_dir(persist_dir),
        vector_store=SimpleVectorStore.from_persist_dir(persist_dir),
        index_store=SimpleIndexStore.from_persist_dir(persist_dir)
    )
    
    # Delete from document store
    if doc_id in storage_context.docstore.docs:
        del storage_context.docstore.docs[doc_id]
    
    # Delete from vector store
    if doc_id in storage_context.vector_store.data:
        del storage_context.vector_store.data[doc_id]
        
        # Update vector index if it exists
        if hasattr(storage_context.vector_store, 'index'):
            storage_context.vector_store.index.delete(doc_id)
    
    # Delete from index store if applicable
    if hasattr(storage_context.index_store, 'index') and doc_id in storage_context.index_store.index:
        del storage_context.index_store.index[doc_id]
    
    # Persist all changes
    storage_context.docstore.persist(persist_dir)
    storage_context.vector_store.persist(persist_dir)
    storage_context.index_store.persist(persist_dir)

# Usage example
delete_document_and_embedding("doc1", persist_dir)
```