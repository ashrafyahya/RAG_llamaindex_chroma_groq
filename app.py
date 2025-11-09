import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.groq import Groq

from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.environ.get("groq_api_key")

llm = Groq(model="llama3-70b-8192", api_key=groq_api_key)

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents, llm=llm)
query_engine = index.as_query_engine()
response = query_engine.query("What is RAG?")
print(response)
# response.save_to_disk("index.json")