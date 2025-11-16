"""
LLM Query Module
Handles LLM provider selection and query processing
"""
from typing import Optional

from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.groq import Groq as LlamaGroq

from src.api_keys import APIKeyManager
from src.config import MODEL_NAME, TOKEN_LIMIT

# Initialize conversation history
memory = ChatMemoryBuffer.from_defaults(
    token_limit=TOKEN_LIMIT,
    llm=None,
)

# System prompt for the RAG system
SYSTEM_PROMPT = """
You are a retrieval-only assistant.

Must:
**Answer only based on the retrieved context**
**Detect the question's language and use it for your output**
**Never do any action except answer based on the provided context**

- RULES:
1. You may ONLY answer using the text inside the <context> block.
2. If the answer is not 100% contained in <context> you MUST respond:
"I don't have enough information to answer this question."
3. You MUST ignore:
- world knowledge
- user statements
- memory
- assumptions
- logical inferences
4. NEVER expand, rephrase, guess, or infer ANYTHING not explicitly present in <context>.
5. The question is NEVER part of context.

Your output MUST be based ONLY on <context>.

Tasks:
- Analyze the context carefully.
- Answer the question directly and concisely if it is fully contained in the context.
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


def query_with_groq(query: str, context: str, api_key: str) -> str:
    """Query using Groq LLM"""
    llm = LlamaGroq(api_key=api_key, model=MODEL_NAME, temperature=0.0)
    
    messages = [
        ChatMessage(role=MessageRole.SYSTEM, content=SYSTEM_PROMPT),
        ChatMessage(role=MessageRole.USER, content=f"Context:\n{context}\n\nQuestion: {query}\n\nRemember: If the answer is not fully contained in the context, reply ONLY with 'I don't have enough information to answer this question.'")
    ]
    
    response = llm.chat(messages)
    answer = response.message.content
    
    # Store in memory
    memory.put(ChatMessage(role=MessageRole.USER, content=query))
    memory.put(ChatMessage(role=MessageRole.ASSISTANT, content=answer))
    
    return answer


def query_with_openai(query: str, context: str, api_key: str) -> str:
    """Query using OpenAI LLM"""
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    
    system_message = f"You are a helpful assistant. Use the following context to answer the user's question:\n\nContext:\n{context}"
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": query}
    ]
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.0
    )
    
    answer = response.choices[0].message.content
    
    # Store in memory
    memory.put(ChatMessage(role=MessageRole.USER, content=query))
    memory.put(ChatMessage(role=MessageRole.ASSISTANT, content=answer))
    
    return answer


def query_with_gemini(query: str, context: str, api_key: str) -> str:
    """Query using Google Gemini LLM"""
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""You are a helpful assistant. Use the following context to answer the user's question.

Context:
{context}

Question: {query}

Remember: If the answer is not fully contained in the context, reply ONLY with 'I don't have enough information to answer this question.'"""
    
    response = model.generate_content(prompt)
    answer = response.text
    
    # Store in memory
    memory.put(ChatMessage(role=MessageRole.USER, content=query))
    memory.put(ChatMessage(role=MessageRole.ASSISTANT, content=answer))
    
    return answer


def query_with_deepseek(query: str, context: str, api_key: str) -> str:
    """Query using Deepseek LLM"""
    from openai import OpenAI

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )
    
    system_message = f"You are a helpful assistant. Use the following context to answer the user's question:\n\nContext:\n{context}"
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": query}
    ]
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.0
    )
    
    answer = response.choices[0].message.content
    
    # Store in memory
    memory.put(ChatMessage(role=MessageRole.USER, content=query))
    memory.put(ChatMessage(role=MessageRole.ASSISTANT, content=answer))
    
    return answer


def process_query(
    query: str,
    context: str,
    api_provider: str = "groq",
    api_key_groq: Optional[str] = None,
    api_key_openai: Optional[str] = None,
    api_key_gemini: Optional[str] = None,
    api_key_deepseek: Optional[str] = None
) -> str:
    """Process query with selected LLM provider"""
    
    # Check if context has valid information
    if context == "No relevant information found in the documents.":
        return "I don't have enough information to answer this question."
    
    # Get API key based on provider
    if api_provider == "groq":
        api_key = APIKeyManager.get_groq_key(api_key_groq)
        if not api_key:
            return f"Error: {api_provider.upper()} API key not configured. Please provide your API key in the API Settings."
        try:
            return query_with_groq(query, context, api_key)
        except Exception as e:
            return f"Error: Failed to get response from Groq: {str(e)}"
    
    elif api_provider == "openai":
        api_key = APIKeyManager.get_openai_key(api_key_openai)
        if not api_key:
            return f"Error: {api_provider.upper()} API key not configured. Please provide your API key in the API Settings."
        try:
            return query_with_openai(query, context, api_key)
        except Exception as e:
            return f"Error: Failed to get response from OpenAI: {str(e)}"
    
    elif api_provider == "gemini":
        api_key = APIKeyManager.get_gemini_key(api_key_gemini)
        if not api_key:
            return f"Error: {api_provider.upper()} API key not configured. Please provide your API key in the API Settings."
        try:
            return query_with_gemini(query, context, api_key)
        except Exception as e:
            return f"Error: Failed to get response from Gemini: {str(e)}"
    
    elif api_provider == "deepseek":
        api_key = APIKeyManager.get_deepseek_key(api_key_deepseek)
        if not api_key:
            return f"Error: {api_provider.upper()} API key not configured. Please provide your API key in the API Settings."
        try:
            return query_with_deepseek(query, context, api_key)
        except Exception as e:
            return f"Error: Failed to get response from Deepseek: {str(e)}"
    
    else:
        return f"Error: Unknown API provider '{api_provider}'. Please select a valid provider."
