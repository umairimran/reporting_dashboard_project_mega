"""
Script to generate a Fernet encryption key for securing sensitive data.
Run this once and add the key to your .env file as ENCRYPTION_KEY.
"""
from cryptography.fernet import Fernet

# Generate a new Fernet key
key = Fernet.generate_key()
print("\n" + "="*80)
print("ENCRYPTION KEY GENERATED")
print("="*80)
print("\nAdd this to your .env file:")
print(f"\nENCRYPTION_KEY={key.decode()}")
print("\n" + "="*80)
print("IMPORTANT: Keep this key secure and never commit it to version control!")
print("="*80 + "\n")
