
"""
Memory Manager Module
Handles advanced memory management with token counting, summarization, and context management
"""
from typing import List, Dict, Tuple, Optional

try:
    import tiktoken
except ImportError:
    print("Warning: tiktoken not installed. Please install it with: pip install tiktoken")
    # Create a fallback tokenizer
    class TikTokenFallback:
        def get_encoding(self, name):
            return self
        def encode(self, text):
            # Simple fallback: count characters and divide by 4 (rough estimate)
            return [0] * (len(text) // 4)
    tiktoken = TikTokenFallback()

from llama_index.core.llms import ChatMessage, MessageRole
from src.config import TOKEN_LIMIT, RECENT_MESSAGES_LIMIT, SUMMARIZE_THRESHOLD, QUESTION_THRESHOLD


class MemoryManager:
    """Advanced memory manager with token counting and summarization"""

    def __init__(self):
        """Initialize the memory manager with token counting capabilities"""
        # Use tiktoken for accurate token counting
        self.encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer
        self.token_limit = TOKEN_LIMIT
        self.recent_messages_limit = RECENT_MESSAGES_LIMIT  # Number of recent messages to include directly
        self.summarize_threshold = SUMMARIZE_THRESHOLD  # 70% of token limit
        self.question_threshold = QUESTION_THRESHOLD  # 20% of token limit for questions

        # Initialize chat history
        self.chat_history: List[ChatMessage] = []

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

    def summarize_messages(self, messages: List[ChatMessage]) -> str:
        """Summarize a list of chat messages"""
        # Format messages for summarization
        formatted_messages = []
        for msg in messages:
            role = "User" if msg.role == MessageRole.USER else "Assistant"
            formatted_messages.append(f"{role}: {msg.content}")

        # Create a simple summary (in a real implementation, this would use an LLM)
        # For now, we'll create a basic summary
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
        context: str
    ) -> Tuple[List[ChatMessage], Optional[str]]:
        """
        Prepare the context for the LLM query

        Returns:
            Tuple of (messages, error_message)
            If error_message is not None, the query should not proceed
        """
        # Calculate token usage
        query_tokens = self.count_tokens(query)
        system_tokens = self.count_tokens(system_prompt)
        context_tokens = self.count_tokens(context)
        
        # Log the token breakdown
        print(f"[CHAT_DEBUG] Token breakdown - Query: {query_tokens}, System: {system_tokens}, Context: {context_tokens}")

        # Check if the query itself is too long (>20% of token limit)
        if query_tokens > self.token_limit * self.question_threshold:
            return [], "Your question is too long. Please ask a shorter question."

        # Calculate remaining tokens for chat history
        remaining_tokens = self.token_limit - query_tokens - system_tokens - context_tokens

        # Check if we've exceeded 70% of token limit with just system prompt, query, and context
        total_without_history = query_tokens + system_tokens + context_tokens
        if total_without_history > self.token_limit * self.summarize_threshold:
            # We need to summarize older messages (4 to end) if they exist
            if len(self.chat_history) > 3:
                older_messages = self.get_older_messages(3, len(self.chat_history))  # Messages 4 to end
                if older_messages:
                    summary = self.summarize_messages(older_messages)
                    summary_tokens = self.count_tokens(summary)

                    # If summary is too long, we might need to further summarize or truncate
                    if summary_tokens > remaining_tokens * 0.5:  # Use at most 50% of remaining tokens
                        # Truncate the summary
                        summary = summary[:int(remaining_tokens * 0.5 * 0.75)]  # Rough estimate
                        summary += "\n[Summary truncated due to length]"

        # Prepare the messages for the LLM
        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content=system_prompt),
        ]

        # Add chat history if available
        if len(self.chat_history) > 0:
            # Get recent messages (up to 3)
            recent_messages = self.get_recent_messages(self.recent_messages_limit)
            recent_tokens = sum(self.count_tokens(msg.content) for msg in recent_messages)
            print(f"[CHAT_DEBUG] Recent messages tokens: {recent_tokens}")

            # Add older messages summary if available
            if len(self.chat_history) > self.recent_messages_limit:
                older_messages = self.get_older_messages(3, len(self.chat_history))  # Messages 4 to end
                if older_messages:
                    summary = self.summarize_messages(older_messages)
                    summary_tokens = self.count_tokens(summary)
                    print(f"[CHAT_DEBUG] Summary tokens: {summary_tokens}")
                    messages.append(
                        ChatMessage(
                            role=MessageRole.SYSTEM,
                            content=f"Previous conversation summary:\n{summary}"
                        )
                    )

            # Add recent messages
            messages.extend(recent_messages)

        # Add current query with context
        query_with_context = f"Context:\n{context}\n\nQuestion: {query}\n\nRemember: If the answer is not fully contained in the context, reply ONLY with 'I don't have enough information to answer this question.'"
        query_context_tokens = self.count_tokens(query_with_context)
        print(f"[CHAT_DEBUG] Query with context tokens: {query_context_tokens}")
        messages.append(ChatMessage(role=MessageRole.USER, content=query_with_context))

        # Check total token count
        total_tokens = 0
        for msg in messages:
            total_tokens += self.count_tokens(msg.content)
            
        # If we're over the token limit, try to reduce the size of the messages
        if total_tokens > self.token_limit:
            # Calculate how much we need to reduce
            excess = total_tokens - self.token_limit
            
            # Try to reduce the summary first if it exists
            for i, msg in enumerate(messages):
                if msg.role == MessageRole.SYSTEM and "Previous conversation summary" in msg.content:
                    # Reduce the summary by removing some content
                    content = msg.content
                    # Remove roughly 75% of the estimated excess tokens
                    reduced_content = content[:-(excess * 3)]
                    reduced_content += "\n[Summary truncated due to length]"
                    messages[i] = ChatMessage(role=MessageRole.SYSTEM, content=reduced_content)
                    break
            
            # Recalculate total tokens
            total_tokens = 0
            for msg in messages:
                total_tokens += self.count_tokens(msg.content)

        # If we're still over the token limit, we need to summarize more messages
        if total_tokens > self.token_limit:
            # If we still have messages beyond the first 15, summarize them as well
            if len(self.chat_history) > 15:
                # Get messages beyond the first 15
                very_old_messages = self.get_older_messages(15, len(self.chat_history))
                if very_old_messages:
                    summary = self.summarize_messages(very_old_messages)
                    # Find and replace the existing summary
                    for i, msg in enumerate(messages):
                        if msg.role == MessageRole.SYSTEM and "Previous conversation summary" in msg.content:
                            messages[i] = ChatMessage(
                                role=MessageRole.SYSTEM,
                                content=f"Previous conversation summary:\n{summary}"
                            )
                            break

                    # Recalculate total tokens
                    total_tokens = 0
                    for msg in messages:
                        total_tokens += self.count_tokens(msg.content)
                    
                    # If still over the limit, try to reduce the summary size
                    if total_tokens > self.token_limit:
                        # Find the summary message and truncate it
                        for i, msg in enumerate(messages):
                            if msg.role == MessageRole.SYSTEM and "Previous conversation summary" in msg.content:
                                # Truncate the summary
                                content = msg.content
                                # Estimate how much to remove
                                excess = total_tokens - self.token_limit
                                # Remove roughly 75% of the estimated excess tokens
                                truncated_content = content[:-(excess * 3)]
                                truncated_content += "\n[Summary truncated due to length]"
                                messages[i] = ChatMessage(role=MessageRole.SYSTEM, content=truncated_content)
                                break
                        
                        # Recalculate total tokens again
                        total_tokens = 0
                        for msg in messages:
                            total_tokens += self.count_tokens(msg.content)
                        
                        # If still over the limit, return error
                        if total_tokens > self.token_limit:
                            return [], "Conversation history is too long. Please start a new conversation."

        # Log the total token count
        total_tokens = 0
        for msg in messages:
            total_tokens += self.count_tokens(msg.content)
        print(f"[CHAT_DEBUG] Total tokens sent to model: {total_tokens}")
        
        return messages, None

    def add_exchange(self, query: str, response: str) -> None:
        """Add a complete user-assistant exchange to the chat history"""
        self.add_message(MessageRole.USER, query)
        self.add_message(MessageRole.ASSISTANT, response)

    def clear_history(self) -> None:
        """Clear the chat history"""
        self.chat_history = []
