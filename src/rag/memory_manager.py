"""
Memory Manager Module
Handles advanced memory management with token counting, summarization, and context management
"""
from typing import List, Optional, Tuple
import time
import tiktoken
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.llms.groq import Groq as LlamaGroq
from openai import InternalServerError, APIError, APIConnectionError, RateLimitError

from src.api_keys import APIKeyManager
from src.config import (MODEL_NAME, QUESTION_THRESHOLD, SUMMARIZE_THRESHOLD,
                        TOKEN_LIMIT)


class MemoryManager:
    """Advanced memory manager with token counting and summarization"""

    def __init__(self):
        """Initialize the memory manager with token counting capabilities"""
        # Use tiktoken for accurate token counting
        self.encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer
        self.token_limit = TOKEN_LIMIT

        self.summarize_threshold = SUMMARIZE_THRESHOLD  # 70% of token limit
        self.question_threshold = QUESTION_THRESHOLD  # 20% of token limit for questions

        # Initialize chat history
        self.chat_history: List[ChatMessage] = []
        
        # Summarization prompt
        self.summarization_prompt = """
        You are an expert at summarizing conversations. Create a concise summary of the following chat conversation between a User and an AI Assistant.

        Requirements:
        - Capture the main topics discussed
        - Include key questions asked and answers provided
        - Maintain the conversational flow and context
        - Keep it concise but informative (aim for 50-200 words)
        - Focus on information that would be useful for future conversation context
        - Use clear, professional language

        Chat conversation to summarize:
        {conversation}

        Provide a clear and concise summary:"""

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string"""
        return len(self.encoding.encode(text))

    def get_chat_history_token_count(self) -> int:
        """Get the total token count of the chat history"""
        total = 0
        for message in self.chat_history:
            total += self.count_tokens(message.content)
        return total

    def add_message(self, role: MessageRole, content: str) -> None:
        """Add a new message to the chat history"""
        self.chat_history.append(ChatMessage(role=role, content=content))

    def get_recent_messages(self, count: int) -> List[ChatMessage]:
        """Get the most recent messages from the chat history"""
        return self.chat_history[-count:] if len(self.chat_history) >= count else self.chat_history

    def get_older_messages(self, start_idx: int, end_idx: int) -> List[ChatMessage]:
        """Get a range of older messages from the chat history"""
        if start_idx >= len(self.chat_history):
            return []

        start = max(0, start_idx)
        end = min(len(self.chat_history), end_idx)
        return self.chat_history[start:end]

    def summarize_messages(self, messages: List[ChatMessage], api_provider: str = "groq", 
                          api_key_groq: Optional[str] = None, api_key_openai: Optional[str] = None,
                          api_key_gemini: Optional[str] = None, api_key_deepseek: Optional[str] = None) -> str:
        """Summarize a list of chat messages using LLM"""
        # Format messages for summarization
        formatted_messages = []
        for msg in messages:
            role = "User" if msg.role == MessageRole.USER else "Assistant"
            formatted_messages.append(f"{role}: {msg.content}")

        conversation_text = "\n".join(formatted_messages)
        
        # Try to get model-based summary using selected provider
        try:
            summary = self._summarize_with_model(conversation_text, api_provider, 
                                                api_key_groq, api_key_openai, 
                                                api_key_gemini, api_key_deepseek)
            if summary:
                return f"Previous conversation summary:\n{summary}"
        except Exception as e:
            print(f"Model summarization failed: {e}")
        
        # Fallback to simple summary if model fails
        summary = "Previous conversation summary:\n"
        
        # Include all messages but truncate if too long
        if len(formatted_messages) > 10:
            # Include first 5 and last 5 messages
            summary += "\n".join(formatted_messages[:5])
            summary += "\n... [previous exchanges] ..."
            summary += "\n".join(formatted_messages[-5:])
            summary += f"\n\nIn total: {len(formatted_messages)} exchanges summarized."
        else:
            # Include all messages if there are fewer than 10
            summary += "\n".join(formatted_messages)

        return summary

    def format_messages_for_prompt(self, messages: List[ChatMessage]) -> str:
        """Format a list of messages for inclusion in a prompt"""
        formatted = []
        for msg in messages:
            role = "User" if msg.role == MessageRole.USER else "Assistant"
            formatted.append(f"{role}: {msg.content}")
        return "\n".join(formatted)

    def prepare_context(
        self,
        query: str,
        system_prompt: str,
        context: str,
        api_provider: str = "groq",
        api_key_groq: Optional[str] = None,
        api_key_openai: Optional[str] = None,
        api_key_gemini: Optional[str] = None,
        api_key_deepseek: Optional[str] = None
    ) -> Tuple[List[ChatMessage], Optional[str], bool]:
        """
        Prepare the context for the LLM query using simplified pipeline

        Returns:
            Tuple of (messages, error_message, needs_summarization)
            If error_message is not None, the query should not proceed
            If needs_summarization is True, UI should show "Summarizing..." state
        """

        # Calculate token usage
        query_tokens = self.count_tokens(query)
        system_tokens = self.count_tokens(system_prompt)
        context_tokens = self.count_tokens(context)
        history_tokens = self.get_chat_history_token_count()

        # Log token usage for monitoring
        print(f"Query tokens: {query_tokens}")
        print(f"System tokens: {system_tokens}")
        print(f"Chat history: {len(self.chat_history)} messages")

        # Check if user question exceeds size limit
        if query_tokens > self.token_limit * self.question_threshold:
            return [], "Your question is too long. Please reduce your input to continue the conversation.", False

        # Check if summarization is needed
        total_estimated_tokens = system_tokens + context_tokens + query_tokens + history_tokens
        seventy_percent_limit = int(self.token_limit * self.summarize_threshold)
        
        needs_summarization = False
        summary_content = None
        
        if total_estimated_tokens > seventy_percent_limit and len(self.chat_history) > 0:
            print(f"Token limit reached ({total_estimated_tokens} > {seventy_percent_limit}), starting summarization")
            
            # Summarize older messages, keep recent exchanges
            if len(self.chat_history) > 6:
                print("Starting chat history summarization...")
                needs_summarization = True
                messages_to_summarize = self.chat_history[:-6]
                summary_content = self.summarize_messages(messages_to_summarize, api_provider, 
                                                        api_key_groq, api_key_openai, 
                                                        api_key_gemini, api_key_deepseek)
                print("Chat history summarization completed")
                
                # Keep only recent messages after summarization
                self.chat_history = self.chat_history[-6:]

        # Prepare the messages for the LLM
        messages = [ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)]
        
        # Add summary if we have one
        if summary_content and "Previous conversation summary:" not in summary_content:
            messages.append(ChatMessage(
                role=MessageRole.SYSTEM,
                content=f"Previous conversation summary:\n{summary_content}"
            ))
        elif summary_content:
            messages.append(ChatMessage(role=MessageRole.SYSTEM, content=summary_content))
        
        # Add remaining chat history
        if len(self.chat_history) > 0:
            messages.extend(self.chat_history)
        
        # Add current query with context
        messages.append(ChatMessage(
            role=MessageRole.USER,
            content=f"Context:\n{context}\n\nQuestion: {query}\n\nRemember: If the answer is not fully contained in the context, reply ONLY with 'I don't have enough information to answer this question.'"
        ))

        # Final validation - ensure we're within token limits
        final_total_tokens = sum(self.count_tokens(msg.content) for msg in messages)
        if final_total_tokens > self.token_limit:
            return [], "The conversation has become too long. Please start a new conversation to continue.", False
        
        print(f"Final token count: {final_total_tokens}")
        return messages, None, needs_summarization

    def add_exchange(self, query: str, response: str) -> None:
        """Add a complete user-assistant exchange to the chat history"""
        self.add_message(MessageRole.USER, query)
        self.add_message(MessageRole.ASSISTANT, response)

    def _summarize_with_model(self, conversation_text: str, api_provider: str = "groq",
                             api_key_groq: Optional[str] = None, api_key_openai: Optional[str] = None,
                             api_key_gemini: Optional[str] = None, api_key_deepseek: Optional[str] = None) -> Optional[str]:
        """Use LLM to create a high-quality summary of the conversation"""
        prompt = self.summarization_prompt.format(conversation=conversation_text)
        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        
        max_retries = 2
        
        try:
            if api_provider == "groq":
                api_key = APIKeyManager.get_groq_key(api_key_groq)
                if not api_key:
                    return None
                llm = LlamaGroq(api_key=api_key, model=MODEL_NAME, temperature=0.1)
                
                # Retry logic for Groq API
                for attempt in range(max_retries + 1):
                    try:
                        response = llm.chat(messages)
                        return response.message.content.strip()
                    except (InternalServerError, APIError) as e:
                        if attempt < max_retries:
                            wait_time = 2 ** attempt
                            print(f"Groq API error during summarization. Retrying in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            print(f"Groq API error during summarization after {max_retries} retries: {e}")
                            return None
                    except Exception as e:
                        print(f"Unexpected error during Groq summarization: {e}")
                        return None
                
            elif api_provider == "openai":
                api_key = APIKeyManager.get_openai_key(api_key_openai)
                if not api_key:
                    return None
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                openai_messages = [{"role": "user", "content": prompt}]
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=openai_messages,
                    temperature=0.1
                )
                return response.choices[0].message.content.strip()
                
            elif api_provider == "gemini":
                api_key = APIKeyManager.get_gemini_key(api_key_gemini)
                if not api_key:
                    return None
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
                return response.text.strip()
                
            elif api_provider == "deepseek":
                api_key = APIKeyManager.get_deepseek_key(api_key_deepseek)
                if not api_key:
                    return None
                from openai import OpenAI
                client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                deepseek_messages = [{"role": "user", "content": prompt}]
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=deepseek_messages,
                    temperature=0.1
                )
                return response.choices[0].message.content.strip()
            else:
                print(f"Unknown API provider: {api_provider}")
                return None
                
        except Exception as e:
            print(f"Error in model summarization with {api_provider}: {e}")
            return None
    

    
    def clear_history(self) -> None:
        """Clear the chat history"""
        self.chat_history = []
