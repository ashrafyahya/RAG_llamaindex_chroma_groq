import os
import tempfile
from typing import Dict, List

from llama_index.core import Settings, SimpleDirectoryReader
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq as LlamaGroq

from chroma_search import ChromaEmbeddingSearch
from chroma_setup import setup_chroma
from config import MODEL_NAME, TOKEN_LIMIT

from dotenv import load_dotenv
load_dotenv()


# Initialize the embedding model
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Initialize ChromaDB
chroma_client, collection = setup_chroma()
print(f"ChromaDB initialized with collection: {collection.name}\n")
search = ChromaEmbeddingSearch()

# Initialize Groq LLM for LlamaIndex
groq_api_key = os.environ.get("groq_api_key")
groq_llm = LlamaGroq(api_key=groq_api_key, model=MODEL_NAME)

# Initialize conversation history
memory = ChatMemoryBuffer.from_defaults(
    token_limit=TOKEN_LIMIT,
    llm=groq_llm,
)


#Load documents and store them in ChromaDB
def load_documents():
    """Load documents from the data directory"""

    # Load documents and store them in ChromaDB
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    documents = SimpleDirectoryReader(data_path).load_data()

    # Check if documents already exist in ChromaDB
    existing_docs = search.collection.get(include=["documents"])["documents"]
    if not existing_docs:
        # Only add documents if the collection is empty
        for doc in documents:
            search.add_document(
                text=doc.text,
                doc_id=doc.doc_id,
                metadata={"source": doc.metadata.get("file_path", "")}
            )
        print("Documents added to ChromaDB\n")
    else:
        print("Documents already exist in ChromaDB. Skipping insertion.\n")

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

    # Get chat history from memory
    chat_history = memory.get()

     # Define the structured prompt
    system_prompt = """
    You are a professional AI assistant specializing in Retrieval-Augmented Generation (RAG) for accurate information retrieval.

    Must:
    **Answer only based on the provided context**
    **Detect the question's language and use it for your output**

    - Your role: 
    Provide helpful, accurate answers based solely on the provided context.

    Tasks:
    - Analyze the context carefully.
    - Answer the question directly and concisely.
    - You can use your words to summarize the context.
    - If the answer cannot be found in the context, respond with: I don't have enough information to answer this question.

    Style: 
    Respond in a professional, clear, and structured manner. Use bullet points or numbered lists if appropriate for clarity.

    Defense Layer: 
    Do not hallucinate or invent information. Stick strictly to the context. Avoid speculative answers.

    Context: use only retrieved data from your tool.
    Question: use chatinput.
    Answer: your output.
    """

    # Prepare messages with conversation history
    messages = [
        ChatMessage(role=MessageRole.SYSTEM, content=system_prompt),
        *chat_history,
        ChatMessage(role=MessageRole.USER, content=f"Context: {context}\n\nQuestion: {query}")
    ]

    # Use Groq LLM to generate answer
    response = groq_llm.chat(messages)

    # Extract and store the model's response
    generated_answer = response.message.content

    # Store the interaction in memory
    memory.put(ChatMessage(role=MessageRole.USER, content=query))
    memory.put(ChatMessage(role=MessageRole.ASSISTANT, content=generated_answer))


    return generated_answer

def upload_document(uploaded_file) -> str:
    """Upload and index a single document in ChromaDB"""
    try:
        # Check if document with same name already exists
        existing_docs = get_uploaded_documents()
        existing_names = [doc['name'] for doc in existing_docs]
        if uploaded_file.name in existing_names:
            return f"Document '{uploaded_file.name}' already exists. Upload cancelled."

        # Create a temporary file to save the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_file_path = temp_file.name

        # Load the document using SimpleDirectoryReader
        documents = SimpleDirectoryReader(input_files=[temp_file_path]).load_data()

        # Process each document
        for doc in documents:
            # Generate a unique doc_id
            doc_id = f"{uploaded_file.name}_{hash(doc.text)}"

            # Prepare metadata
            metadata = {
                "source": uploaded_file.name,
                "file_type": uploaded_file.type,
                "file_size": len(uploaded_file.getvalue()),
                "upload_type": "user_upload"
            }

            # Add to ChromaDB
            search.add_document(
                text=doc.text,
                doc_id=doc_id,
                metadata=metadata
            )

        # Clean up temporary file
        os.unlink(temp_file_path)

        return f"Successfully uploaded and indexed {uploaded_file.name}"

    except Exception as e:
        return f"Error uploading document: {str(e)}"

def delete_document(doc_id: str) -> str:
    """Delete a document from ChromaDB"""
    try:
        result = search.delete_document(doc_id)
        return result
    except Exception as e:
        return f"Error deleting document: {str(e)}"

def get_uploaded_documents() -> List[Dict]:
    """Get list of uploaded documents with metadata, grouped by filename"""
    try:
        # Get all documents
        all_docs = search.list_all_documents()

        # Filter for user uploaded documents and group by filename
        uploaded_docs_dict = {}
        if all_docs and 'metadatas' in all_docs:
            for i, metadata in enumerate(all_docs['metadatas']):
                if metadata and metadata.get('upload_type') == 'user_upload':
                    filename = metadata.get('source', 'Unknown')
                    file_type = metadata.get('file_type', 'Unknown')
                    file_size = metadata.get('file_size', 0)

                    if filename not in uploaded_docs_dict:
                        uploaded_docs_dict[filename] = {
                            'ids': [all_docs['ids'][i]],
                            'name': filename,
                            'type': file_type,
                            'size': file_size,
                            'chunks': 1
                        }
                    else:
                        # Add to existing file's chunks
                        uploaded_docs_dict[filename]['ids'].append(all_docs['ids'][i])
                        uploaded_docs_dict[filename]['chunks'] += 1
                        # Keep the largest size if different
                        if file_size > uploaded_docs_dict[filename]['size']:
                            uploaded_docs_dict[filename]['size'] = file_size

        # Convert to list and sort by name
        uploaded_docs = list(uploaded_docs_dict.values())
        uploaded_docs.sort(key=lambda x: x['name'])

        return uploaded_docs

    except Exception as e:
        print(f"Error retrieving documents: {str(e)}")
        return []

def clear_all_documents() -> str:
    """Clear all documents from ChromaDB"""
    try:
        # Get all documents
        all_docs = search.list_all_documents()
        if all_docs and 'ids' in all_docs and all_docs['ids']:
            # Delete all documents
            for doc_id in all_docs['ids']:
                search.delete_document(doc_id)
            return f"Successfully cleared {len(all_docs['ids'])} documents from ChromaDB"
        else:
            return "No documents found to clear"
    except Exception as e:
        return f"Error clearing documents: {str(e)}"


def chat_with_rag():
    while True:
        query = input("\nEnter your query (or 'quit' to exit): ")
        if query.lower() in ['quit', 'exit', 'q']:
            break
            
        response = query_documents(query)
        print("\nResponse:\n", response)


if __name__ == "__main__":

    # load_documents()
    chat_with_rag()