# ===================================
# utils/validators.py
# ===================================
import re
from typing import Optional

def validate_mobile(mobile: str) -> bool:
    """Validate mobile number format"""
    pattern = r"^\+?[1-9]\d{1,14}$"
    return bool(re.match(pattern, mobile))

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def validate_password_strength(password: str) -> dict:
    """Validate password strength"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one digit")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }

def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """Sanitize string input"""
    if not value:
        return ""
    
    # Remove extra whitespace
    value = value.strip()
    
    # Truncate if needed
    if max_length and len(value) > max_length:
        value = value[:max_length]
    
    return value