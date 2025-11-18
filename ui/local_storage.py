"""
Local storage utilities for persisting API keys and user preferences
Uses encryption for secure storage and retrieval of API keys
"""

import base64
import json
import os
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class LocalStorage:
    """Handle persistent storage of API keys and settings with encryption"""
    
    def __init__(self):
        # Create a .streamlit_cache directory in the project root for storing sensitive data
        self.storage_dir = Path.home() / ".streamlit_cache" / "agentic_ai"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.storage_file = self.storage_dir / "api_keys.json"
        # Use machine's username as part of the encryption key derivation
        self.salt = os.getenv("USERNAME", "user").encode('utf-8')
        self._cipher = self._get_cipher()
    
    def _get_cipher(self) -> Fernet:
        """Generate a Fernet cipher using PBKDF2 key derivation"""
        # Derive a key from the username using PBKDF2HMAC
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.salt))
        return Fernet(key)
    
    def _encrypt_api_key(self, api_key: str) -> str:
        """Encrypt an API key using Fernet encryption"""
        if not api_key or not api_key.strip():
            return ""
        encrypted = self._cipher.encrypt(api_key.encode('utf-8'))
        return encrypted.decode('utf-8')
    
    def _decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt an API key using Fernet encryption"""
        if not encrypted_key or not encrypted_key.strip():
            return ""
        try:
            decrypted = self._cipher.decrypt(encrypted_key.encode('utf-8'))
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"Error decrypting API key: {e}")
            return ""
    
    def load_api_keys(self):
        """Load API keys from local storage - decrypts them"""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    encrypted_keys = data.get("api_keys", {
                        "groq": "",
                        "openai": "",
                        "gemini": "",
                        "deepseek": ""
                    })
                    # Decrypt all keys
                    return {
                        provider: self._decrypt_api_key(key)
                        for provider, key in encrypted_keys.items()
                    }
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
        """Save API keys to local storage - encrypts them first"""
        try:
            # Encrypt all API keys before saving
            encrypted_keys = {
                provider: self._encrypt_api_key(key)
                for provider, key in api_keys.items()
            }
            data = {"api_keys": encrypted_keys}
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving API keys: {e}")
            return False
    
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

