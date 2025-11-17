
"""
Memory Manager Module
Handles advanced memory management with token counting, summarization, and context management
"""
from typing import Dict, List, Optional, Tuple

import tiktoken
from llama_index.core.llms import ChatMessage, MessageRole

from src.config import (QUESTION_THRESHOLD, RECENT_MESSAGES_LIMIT,
                        SUMMARIZE_THRESHOLD, TOKEN_LIMIT)


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

        # Debug output for testing
        print(f"[MEMORY_DEBUG] Query tokens: {query_tokens}")
        print(f"[MEMORY_DEBUG] System tokens: {system_tokens}")
        print(f"[MEMORY_DEBUG] Context tokens: {context_tokens}")
        print(f"[MEMORY_DEBUG] Chat history length: {len(self.chat_history)} messages")
        history_tokens = self.get_chat_history_token_count()
        print(f"[MEMORY_DEBUG] Chat history total tokens: {history_tokens}")

        # Check if the query itself is too long (>20% of token limit)
        if query_tokens > self.token_limit * self.question_threshold:
            return [], "Your question is too long. Please ask a shorter question."

        # Prepare the messages for the LLM
        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content=system_prompt),
        ]

        # Add chat history if available
        if len(self.chat_history) > 0:
            # Get recent messages (up to 3)
            recent_messages = self.get_recent_messages(self.recent_messages_limit)

            # Add older messages summary if available and we have enough messages
            if len(self.chat_history) > self.recent_messages_limit:
                older_messages = self.get_older_messages(3, 15)  # Messages 4-15
                if older_messages:
                    summary = self.summarize_messages(older_messages)
                    messages.append(
                        ChatMessage(
                            role=MessageRole.SYSTEM,
                            content=f"Previous conversation summary:\n{summary}"
                        )
                    )

            # Add recent messages
            messages.extend(recent_messages)

        # Add current query with context
        messages.append(
            ChatMessage(
                role=MessageRole.USER,
                content=f"Context:\n{context}\n\nQuestion: {query}\n\nRemember: If the answer is not fully contained in the context, reply ONLY with 'I don't have enough information to answer this question.'"
            )
        )

        # Check total token count
        total_tokens = 0
        for msg in messages:
            total_tokens += self.count_tokens(msg.content)

        # If over token limit, try to reduce context or summarize more aggressively
        if total_tokens > self.token_limit:
            # For small histories (<10 messages), allow some flexibility
            if len(self.chat_history) < 10:
                # Try truncating context to fit
                max_context_tokens = self.token_limit - (total_tokens - context_tokens) - 100  # Leave some buffer
                if max_context_tokens > 100:  # Minimum useful context
                    truncated_context = context
                    while self.count_tokens(truncated_context) > max_context_tokens and len(truncated_context) > 100:
                        # Truncate by removing the last 10% of content
                        truncate_point = int(len(truncated_context) * 0.9)
                        truncated_context = truncated_context[:truncate_point] + "\n[Context truncated due to length]"

                    # Update the user message with truncated context
                    for i, msg in enumerate(messages):
                        if msg.role == MessageRole.USER:
                            messages[i] = ChatMessage(
                                role=MessageRole.USER,
                                content=f"Context:\n{truncated_context}\n\nQuestion: {query}\n\nRemember: If the answer is not fully contained in the context, reply ONLY with 'I don't have enough information to answer this question.'"
                            )
                            break

                    # Recalculate total tokens
                    total_tokens = 0
                    for msg in messages:
                        total_tokens += self.count_tokens(msg.content)

            # If still over limit and we have messages beyond 15, summarize them
            if total_tokens > self.token_limit and len(self.chat_history) > 15:
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

            # Final check: if still over limit, summarize more aggressively instead of error
            if total_tokens > self.token_limit:
                # For any history size, try to summarize everything beyond recent messages
                if len(self.chat_history) > self.recent_messages_limit:
                    # Summarize all messages beyond the recent ones (4 to end)
                    all_older_messages = self.get_older_messages(self.recent_messages_limit, len(self.chat_history))
                    if all_older_messages:
                        summary = self.summarize_messages(all_older_messages)
                        # Replace any existing summary or add new one
                        summary_found = False
                        for i, msg in enumerate(messages):
                            if msg.role == MessageRole.SYSTEM and "Previous conversation summary" in msg.content:
                                messages[i] = ChatMessage(
                                    role=MessageRole.SYSTEM,
                                    content=f"Previous conversation summary:\n{summary}"
                                )
                                summary_found = True
                                break
                        if not summary_found:
                            # Insert summary after system prompt
                            messages.insert(1, ChatMessage(
                                role=MessageRole.SYSTEM,
                                content=f"Previous conversation summary:\n{summary}"
                            ))

                        # Recalculate total tokens
                        total_tokens = 0
                        for msg in messages:
                            total_tokens += self.count_tokens(msg.content)

                        # If still over limit, truncate the summary
                        if total_tokens > self.token_limit:
                            excess = total_tokens - self.token_limit
                            for i, msg in enumerate(messages):
                                if msg.role == MessageRole.SYSTEM and "Previous conversation summary" in msg.content:
                                    content = msg.content
                                    # Truncate summary to fit
                                    max_summary_tokens = self.count_tokens(content) - excess - 50  # Buffer
                                    if max_summary_tokens > 100:
                                        truncated_summary = content
                                        while self.count_tokens(truncated_summary) > max_summary_tokens and len(truncated_summary) > 200:
                                            truncate_point = int(len(truncated_summary) * 0.9)
                                            truncated_summary = truncated_summary[:truncate_point] + "\n[Summary truncated due to length]"
                                        messages[i] = ChatMessage(
                                            role=MessageRole.SYSTEM,
                                            content=truncated_summary
                                        )
                                    break

        # Final debug output showing total tokens sent to model
        final_total_tokens = sum(self.count_tokens(msg.content) for msg in messages)
        print(f"[MEMORY_DEBUG] Final total tokens sent to model: {final_total_tokens}")

        return messages, None

    def add_exchange(self, query: str, response: str) -> None:
        """Add a complete user-assistant exchange to the chat history"""
        self.add_message(MessageRole.USER, query)
        self.add_message(MessageRole.ASSISTANT, response)

    def clear_history(self) -> None:
        """Clear the chat history"""
        self.chat_history = []
