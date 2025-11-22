#!/usr/bin/env python3
"""Test JWT token functionality"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.security import create_access_token, decode_token

# Test JWT functionality
def test_jwt():
    print("Testing JWT functionality...")

    # Create a token
    user_id = "68d28cd824dc34fc4acb3961"
    token = create_access_token(user_id)
    print(f"Created token: {token}")

    # Decode the token
    try:
        payload = decode_token(token)
        print(f"Decoded payload: {payload}")
        print(f"User ID from token: {payload.get('sub')}")
        print("✅ JWT functionality working correctly")
        return True
    except Exception as e:
        print(f"❌ JWT error: {e}")
        return False

if __name__ == "__main__":
    test_jwt()