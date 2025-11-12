import os
from llama_index.core import SimpleDirectoryReader
from savingEmbeddingsLocal import load_or_create_index

# Load or create the index
index = load_or_create_index()

query_engine = index.as_query_engine()
response = query_engine.query("What is RAG?")
print(response)
