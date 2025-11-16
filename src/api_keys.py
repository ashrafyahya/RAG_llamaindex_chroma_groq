"""
API Key Management Module
Handles user-provided API keys only - no fallback to environment variables
"""
from typing import Optional


class APIKeyManager:
    """Manage API keys from user input only"""
    
    @staticmethod
    def get_groq_key(user_key: Optional[str] = None) -> Optional[str]:
        """Get Groq API key from user input only"""
        if user_key and user_key.strip():
            return user_key.strip()
        return None
    
    @staticmethod
    def get_openai_key(user_key: Optional[str] = None) -> Optional[str]:
        """Get OpenAI API key from user input only"""
        if user_key and user_key.strip():
            return user_key.strip()
        return None
    
    @staticmethod
    def get_gemini_key(user_key: Optional[str] = None) -> Optional[str]:
        """Get Gemini API key from user input only"""
        if user_key and user_key.strip():
            return user_key.strip()
        return None
    
    @staticmethod
    def get_deepseek_key(user_key: Optional[str] = None) -> Optional[str]:
        """Get Deepseek API key from user input only"""
        if user_key and user_key.strip():
            return user_key.strip()
        return None