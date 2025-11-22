# ===================================
# utils/encryption.py
# ===================================
from cryptography.fernet import Fernet
from backend.core.config import settings
import base64
import hashlib

def get_encryption_key() -> bytes:
    """Generate encryption key from secret key"""
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return base64.urlsafe_b64encode(key)

def encrypt_string(value: str) -> str:
    """Encrypt a string value"""
    try:
        fernet = Fernet(get_encryption_key())
        encrypted_value = fernet.encrypt(value.encode())
        return encrypted_value.decode()
    except Exception:
        return value  # Return original if encryption fails

def decrypt_string(encrypted_value: str) -> str:
    """Decrypt a string value"""
    try:
        fernet = Fernet(get_encryption_key())
        decrypted_value = fernet.decrypt(encrypted_value.encode())
        return decrypted_value.decode()
    except Exception:
        return encrypted_value  # Return original if decryption fails
