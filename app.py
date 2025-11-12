import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding  
from llama_index.core import Settings

from dotenv import load_dotenv


load_dotenv()
groq_api_key = os.environ.get("groq_api_key")


# Set the global settings & Configure all components in one place
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.chunk_size = 512
Settings.chunk_overlap = 50
Settings.llm = Groq(model="llama-3.1-8b-instant", api_key=groq_api_key)


# Loading documents from a local directory
documents = SimpleDirectoryReader("data").load_data()

# processe the input documents to convert them into numerical vector representations
# The VectorStoreIndex.from_documents() method typically creates an in-memory index
index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()
response = query_engine.query("What is RAG?")
print(response)
