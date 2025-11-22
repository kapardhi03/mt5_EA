#!/usr/bin/env python3
"""
Simple OTP test to debug the issue
"""
import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_otp_flow():
    client = httpx.AsyncClient(timeout=30.0)
    
    mobile = "+1234567890"
    otp = "123456"  # Fixed OTP for testing
    
    try:
        # Send OTP
        print(f"1. Sending OTP for {mobile}")
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/send-otp",
            json={
                "mobile_or_email": mobile,
                "otp_type": "mobile"
            }
        )
        
        result = response.json()
        print(f"Send response: {result}")
        
        if result.get("success"):
            # Get the actual OTP from response
            actual_otp = result.get("data", {}).get("otp")
            print(f"Actual OTP: {actual_otp}")
            
            # Verify with the actual OTP
            print(f"2. Verifying OTP {actual_otp}")
            verify_response = await client.post(
                f"{BASE_URL}/api/v1/auth/verify-otp",
                json={
                    "mobile_or_email": mobile,
                    "otp": actual_otp,
                    "otp_type": "mobile"
                }
            )
            
            verify_result = verify_response.json()
            print(f"Verify response: {verify_result}")
            
            # Also try with a hardcoded OTP
            print(f"3. Verifying with hardcoded OTP 123456")
            verify_response2 = await client.post(
                f"{BASE_URL}/api/v1/auth/verify-otp",
                json={
                    "mobile_or_email": mobile,
                    "otp": "123456",
                    "otp_type": "mobile"
                }
            )
            
            verify_result2 = verify_response2.json()
            print(f"Hardcoded verify response: {verify_result2}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_otp_flow())


