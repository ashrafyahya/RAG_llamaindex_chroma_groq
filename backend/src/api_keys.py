"""
API Key Management Module
Handles user-provided API keys with simple in-memory storage
"""
from typing import Dict, Optional


class APIKeyManager:
    """Manage API keys with in-memory storage"""
    
    def __init__(self):
        """Initialize API key storage"""
        self.api_keys: Dict[str, str] = {
            "groq": "",
            "openai": "",
            "gemini": "",
            "deepseek": ""
        }
        self.selected_provider: str = "groq"
    
    def save_api_key(self, provider: str, api_key: str) -> None:
        """Save API key for a provider"""
        if provider in self.api_keys:
            self.api_keys[provider] = api_key
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider"""
        return self.api_keys.get(provider, "")
    
    def save_selected_provider(self, provider: str) -> None:
        """Save the selected provider"""
        if provider in self.api_keys:
            self.selected_provider = provider
    
    def get_selected_provider(self) -> str:
        """Get the selected provider"""
        return self.selected_provider
    
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