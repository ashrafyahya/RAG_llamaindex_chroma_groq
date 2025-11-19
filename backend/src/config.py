"""
Configuration Module
Central configuration settings for the RAG system
"""

# LLM Model Configuration
MODEL_NAME = "llama-3.1-8b-instant"  # Default model for Groq API
TOKEN_LIMIT = 8000  # Maximum tokens per request
MAX_TOKENS = 2048   # Maximum tokens in response

# Memory Management Thresholds
SUMMARIZE_THRESHOLD = 0.7  # Trigger summarization at 70% of token limit
QUESTION_THRESHOLD = 0.2   # Maximum question size as fraction of token limit

