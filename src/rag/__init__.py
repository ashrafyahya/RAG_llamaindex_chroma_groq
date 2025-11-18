"""
RAG (Retrieval-Augmented Generation) Module

Provides core RAG functionality including memory management,
document retrieval, and LLM query processing.
"""
from .memory_manager import MemoryManager

# Global memory manager instance for conversation tracking
memory_manager = MemoryManager()
