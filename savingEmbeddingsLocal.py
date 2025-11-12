import os
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding  
from llama_index.llms.groq import Groq

from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.environ.get("groq_api_key")


# Set the global settings & Configure all components in one place
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.chunk_size = 512
Settings.chunk_overlap = 50
Settings.llm = Groq(model="llama-3.1-8b-instant", api_key=groq_api_key)
        
# Directory to store the index
persist_dir = "./storage"

def load_or_create_index():
    # Check if index already exists
    if os.path.exists(persist_dir):
        # Load existing index
        storage_context = StorageContext.from_defaults(
            docstore=SimpleDocumentStore.from_persist_dir(persist_dir),
            vector_store=SimpleVectorStore.from_persist_dir(persist_dir),
            index_store=SimpleIndexStore.from_persist_dir(persist_dir)
        )
        index = load_index_from_storage(storage_context)
    else:
        # Create new index and save it
        documents = SimpleDirectoryReader("data").load_data()
        # Create storage context
        storage_context = StorageContext.from_defaults(
            docstore=SimpleDocumentStore(),
            vector_store=SimpleVectorStore(),
            index_store=SimpleIndexStore()
        )

        # Create index with storage context
        index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

        # Persist the index
        index.storage_context.persist(persist_dir)
    
    return index

# Use the function
index = load_or_create_index()
