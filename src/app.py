from chroma_setup import setup_chroma
from llama_index.core import Settings
from chroma_search import ChromaEmbeddingSearch
from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from groq import Groq
import os

from dotenv import load_dotenv
load_dotenv()

# Initialize the embedding model
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Initialize ChromaDB
chroma_client, collection = setup_chroma()
print(f"ChromaDB initialized with collection: {collection.name}")
search = ChromaEmbeddingSearch()

# Initialize Groq client
groq_api_key = os.environ.get("groq_api_key")
groq_client = Groq(api_key=groq_api_key)


# Load documents and store them in ChromaDB
documents = SimpleDirectoryReader("..\\data").load_data()
for doc in documents:
    search.add_document(
        text=doc.text,
        doc_id=doc.doc_id,
        metadata={"source": doc.metadata.get("file_path", "")}
    )
    

def format_search_results(results, query: str, n_results: int = 3):
    """Format search results into a coherent answer"""
    if not results or 'documents' not in results or not results['documents'][0]:
        return "No relevant information found in the documents."
    
    # Get the most relevant documents
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    
    # Format the results
    formatted_answer = f"\n\nBased on your question: '{query}'\n\n"
    formatted_answer += "Here are the relevant findings:\n\n"
    
    for i, (doc, meta) in enumerate(zip(documents, metadatas)):
        formatted_answer += f"Source {i+1}: {meta['source']}\n"
        formatted_answer += f"Content:\n{doc}\n\n"
    
    return formatted_answer

# Query the database
def query_documents(query: str, n_results: int = 3):
    """Query ChromaDB and format the results"""
    # Get relevant documents
    results = search.collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
     # Format context from documents
    context = format_search_results(results, query)
    
    # Use Groq to generate answer
    response = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions based on the provided context."
            },
            {
                "role": "user",
                "content": f"Context: {context}\n\nQuestion: {query}"
            }
        ],
        model="llama-3.1-8b-instant" 
    )
    
    return response.choices[0].message.content


query = "In three sentences tell me what is RAG?"
response = query_documents(query)
print("response:", response)

