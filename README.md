# Retrieval-Augmented Generation (RAG) system using ChromaDB, LlamaIndex and Groq

This project demonstrates the implementation of a Retrieval-Augmented Generation (RAG) system using ChromaDB for vector storage, LlamaIndex for document indexing, and Groq for LLM inference. The system enables efficient retrieval and generation of responses based on a collection of documents about Agentic AI.

## Project Overview

The project builds a research assistant that can answer questions about Agentic AI by retrieving relevant information from a document collection and generating responses using a language model. This implementation combines several key technologies:

- **Vector Database**: ChromaDB for storing and retrieving document embeddings
- **Embedding Model**: HuggingFace's BGE-small-en-v1.5 for document embeddings
- **LLM Interface**: Groq API for fast language model inference
- **Document Processing**: LlamaIndex for efficient document loading and processing

## Architecture

The system follows a standard RAG architecture:

1. **Document Loading**: Documents are loaded from the data directory using LlamaIndex's SimpleDirectoryReader
2. **Embedding Generation**: Documents are embedded using HuggingFace's BGE model
3. **Vector Storage**: Embeddings are stored in ChromaDB for efficient similarity search
4. **Query Processing**: When a user asks a question, the system:
   - Embeds the query using the same embedding model
   - Retrieves relevant documents from ChromaDB
   - Formats the retrieved documents as context
   - Generates an answer using Groq's LLM with the provided context

## Key Components

- `app.py`: Main application that loads documents, initializes components, and processes queries
- `chroma_setup.py`: Sets up the ChromaDB client and collection
- `chroma_search.py`: Provides a wrapper class for ChromaDB operations including search, add, update, and delete
- `groq_testing.py`: Simple test script for Groq API functionality

## Data

The project uses a collection of documents about Agentic AI, stored in the `data` directory. These documents cover topics such as:
- Introduction to Agentic AI
- Vector databases and semantic retrieval
- Prompt engineering techniques
- Memory management strategies
- System prompts
- Real-world applications of Agentic AI

## Usage

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   Create a `.env` file with your Groq API key:
   ```
   groq_api_key=your_api_key_here
   ```

3. Run the application:
   ```
   python src/app.py
   ```

## Future Work

Based on the TODO.md, future improvements include:
- Implementing prompting with templates and system prompts
- Enhancing data protection and memory management for the model
- Further optimization of the RAG pipeline for better performance

## Technologies Used

- **ChromaDB**: Vector database for storing document embeddings
- **LlamaIndex**: Framework for building LLM applications
- **HuggingFace**: For embedding models
- **Groq**: Fast language model inference API
- **Python-dotenv**: For environment variable management