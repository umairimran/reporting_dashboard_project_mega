"""
Encryption utilities for sensitive data like API keys.
"""
from cryptography.fernet import Fernet
from app.core.config import settings
from app.core.logging import logger


class EncryptionService:
    """Service for encrypting and decrypting sensitive data."""
    
    @staticmethod
    def _get_cipher():
        """Get Fernet cipher instance using the encryption key from settings."""
        return Fernet(settings.ENCRYPTION_KEY.encode())
    
    @staticmethod
    def encrypt(plain_text: str) -> str:
        """
        Encrypt a plain text string.
        
        Args:
            plain_text: The text to encrypt
            
        Returns:
            Encrypted text as a string
        """
        if not plain_text:
            return plain_text
        
        try:
            cipher = EncryptionService._get_cipher()
            encrypted_bytes = cipher.encrypt(plain_text.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise ValueError("Failed to encrypt data")
    
    @staticmethod
    def decrypt(encrypted_text: str) -> str:
        """
        Decrypt an encrypted string.
        
        Args:
            encrypted_text: The encrypted text
            
        Returns:
            Decrypted plain text
        """
        if not encrypted_text:
            return encrypted_text
        
        try:
            cipher = EncryptionService._get_cipher()
            decrypted_bytes = cipher.decrypt(encrypted_text.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise ValueError("Failed to decrypt data")


def encrypt_api_key(api_key: str) -> str:
    """Convenience function to encrypt an API key."""
    return EncryptionService.encrypt(api_key)


def decrypt_api_key(encrypted_key: str) -> str:
    """Convenience function to decrypt an API key."""
    return EncryptionService.decrypt(encrypted_key)
