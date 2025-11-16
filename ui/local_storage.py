"""
Local storage utilities for persisting API keys and user preferences
"""

import hashlib
import json
import os
from pathlib import Path


class LocalStorage:
    """Handle persistent storage of API keys and settings with hashing"""
    
    def __init__(self):
        # Create a .streamlit_cache directory in the project root for storing sensitive data
        self.storage_dir = Path.home() / ".streamlit_cache" / "agentic_ai"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.storage_file = self.storage_dir / "api_keys.json"
        # Use machine's username as part of the salt for additional security
        self.salt = os.getenv("USERNAME", "user")
    
    @staticmethod
    def _hash_api_key(api_key: str, salt: str) -> str:
        """Hash an API key using SHA256 with salt"""
        if not api_key or not api_key.strip():
            return ""
        # Combine salt + api_key for hashing
        to_hash = f"{salt}{api_key}".encode('utf-8')
        return hashlib.sha256(to_hash).hexdigest()
    
    def load_api_keys(self):
        """Load API keys from local storage - returns hashed keys"""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    return data.get("api_keys", {
                        "groq": "",
                        "openai": "",
                        "gemini": "",
                        "deepseek": ""
                    })
            except (json.JSONDecodeError, IOError):
                return {
                    "groq": "",
                    "openai": "",
                    "gemini": "",
                    "deepseek": ""
                }
        return {
            "groq": "",
            "openai": "",
            "gemini": "",
            "deepseek": ""
        }
    
    def save_api_keys(self, api_keys: dict):
        """Save API keys to local storage - hashes them first"""
        try:
            # Hash all API keys before saving
            hashed_keys = {
                provider: self._hash_api_key(key, self.salt)
                for provider, key in api_keys.items()
            }
            data = {"api_keys": hashed_keys}
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving API keys: {e}")
            return False
    
    def verify_api_key(self, provider: str, api_key: str) -> bool:
        """Verify if a provided API key matches the stored hashed version"""
        stored_hash = self.load_api_keys().get(provider, "")
        if not stored_hash:
            return False
        provided_hash = self._hash_api_key(api_key, self.salt)
        return provided_hash == stored_hash
    
    def load_selected_provider(self):
        """Load the last selected provider"""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    return data.get("selected_provider", "groq")
            except (json.JSONDecodeError, IOError):
                return "groq"
        return "groq"
    
    def save_selected_provider(self, provider: str):
        """Save the selected provider"""
        try:
            # Load existing data
            if self.storage_file.exists():
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {"api_keys": {}}
            
            # Update provider
            data["selected_provider"] = provider
            
            # Save back
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving provider: {e}")
            return False


# Global instance
_storage = LocalStorage()


def get_storage():
    """Get the global storage instance"""
    return _storage

