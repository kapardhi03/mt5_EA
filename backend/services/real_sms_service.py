"""
Real SMS service for MT5 Copy Trading Platform
Supports multiple SMS providers with real phone number integration
"""
import os
import json
import asyncio
import aiohttp
from typing import Dict, Optional
from datetime import datetime
from backend.core.config import settings

class RealSMSService:
    def __init__(self):
        self.providers = {
            "twilio": self._send_twilio_sms,
            "fast2sms": self._send_fast2sms,
            "textlocal": self._send_textlocal_sms,
            "msg91": self._send_msg91_sms
        }
        self.active_provider = self._detect_provider()

    def _detect_provider(self) -> str:
        """Detect which SMS provider is configured"""
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            return "twilio"
        elif os.getenv("FAST2SMS_API_KEY"):
            return "fast2sms"
        elif os.getenv("TEXTLOCAL_API_KEY"):
            return "textlocal"
        elif os.getenv("MSG91_API_KEY"):
            return "msg91"
        else:
            return "demo"

    async def send_sms(self, phone_number: str, message: str) -> Dict:
        """Send SMS using configured provider"""
        try:
            # Clean phone number
            phone_number = self._clean_phone_number(phone_number)

            if self.active_provider == "demo":
                return await self._send_demo_sms(phone_number, message)

            provider_func = self.providers.get(self.active_provider)
            if provider_func:
                return await provider_func(phone_number, message)
            else:
                return {"status": False, "message": "No SMS provider configured"}

        except Exception as e:
            return {"status": False, "message": f"SMS sending failed: {str(e)}"}

    def _clean_phone_number(self, phone_number: str) -> str:
        """Clean and format phone number"""
        # Remove all non-digit characters except +
        cleaned = ''.join(c for c in phone_number if c.isdigit() or c == '+')

        # Add + if not present and starts with country code
        if not cleaned.startswith('+'):
            if cleaned.startswith('91') and len(cleaned) == 12:  # India
                cleaned = '+' + cleaned
            elif cleaned.startswith('1') and len(cleaned) == 11:  # US/Canada
                cleaned = '+' + cleaned
            elif len(cleaned) == 10:  # Assume India without country code
                cleaned = '+91' + cleaned
            else:
                cleaned = '+' + cleaned

        return cleaned

    async def _send_demo_sms(self, phone_number: str, message: str) -> Dict:
        """Demo SMS service - logs message instead of sending"""
        print(f"📱 DEMO SMS Service:")
        print(f"To: {phone_number}")
        print(f"Message: {message}")
        print(f"Time: {datetime.now()}")

        return {
            "status": True,
            "message": f"Demo SMS sent to {phone_number}",
            "provider": "demo",
            "message_id": f"demo_{int(datetime.now().timestamp())}"
        }

    async def _send_twilio_sms(self, phone_number: str, message: str) -> Dict:
        """Send SMS using Twilio"""
        try:
            import base64
            from twilio.rest import Client

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            message_obj = client.messages.create(
                body=message,
                from_=settings.TWILIO_FROM_NUMBER,
                to=phone_number
            )

            return {
                "status": True,
                "message": "SMS sent successfully via Twilio",
                "provider": "twilio",
                "message_id": message_obj.sid
            }

        except Exception as e:
            return {"status": False, "message": f"Twilio SMS failed: {str(e)}"}

    async def _send_fast2sms(self, phone_number: str, message: str) -> Dict:
        """Send SMS using Fast2SMS (India)"""
        try:
            api_key = os.getenv("FAST2SMS_API_KEY")
            if not api_key:
                return {"status": False, "message": "Fast2SMS API key not configured"}

            # Remove country code for Indian numbers
            if phone_number.startswith('+91'):
                phone_number = phone_number[3:]

            url = "https://www.fast2sms.com/dev/bulkV2"

            payload = {
                "authorization": api_key,
                "message": message,
                "language": "english",
                "route": "q",
                "numbers": phone_number,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=payload) as response:
                    result = await response.json()

                    if result.get("return"):
                        return {
                            "status": True,
                            "message": "SMS sent successfully via Fast2SMS",
                            "provider": "fast2sms",
                            "message_id": result.get("request_id")
                        }
                    else:
                        return {"status": False, "message": f"Fast2SMS error: {result.get('message', 'Unknown error')}"}

        except Exception as e:
            return {"status": False, "message": f"Fast2SMS failed: {str(e)}"}

    async def _send_textlocal_sms(self, phone_number: str, message: str) -> Dict:
        """Send SMS using TextLocal"""
        try:
            api_key = os.getenv("TEXTLOCAL_API_KEY")
            if not api_key:
                return {"status": False, "message": "TextLocal API key not configured"}

            url = "https://api.textlocal.in/send/"

            payload = {
                "apikey": api_key,
                "numbers": phone_number,
                "message": message,
                "sender": "MTTLNT"  # Your sender ID
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=payload) as response:
                    result = await response.json()

                    if result.get("status") == "success":
                        return {
                            "status": True,
                            "message": "SMS sent successfully via TextLocal",
                            "provider": "textlocal",
                            "message_id": result.get("messages", [{}])[0].get("id")
                        }
                    else:
                        return {"status": False, "message": f"TextLocal error: {result.get('errors', [{}])[0].get('message', 'Unknown error')}"}

        except Exception as e:
            return {"status": False, "message": f"TextLocal failed: {str(e)}"}

    async def _send_msg91_sms(self, phone_number: str, message: str) -> Dict:
        """Send SMS using MSG91"""
        try:
            api_key = os.getenv("MSG91_API_KEY")
            if not api_key:
                return {"status": False, "message": "MSG91 API key not configured"}

            # Remove + from phone number
            if phone_number.startswith('+'):
                phone_number = phone_number[1:]

            url = f"https://api.msg91.com/api/v5/otp"

            headers = {
                "authkey": api_key,
                "Content-Type": "application/json"
            }

            payload = {
                "template_id": os.getenv("MSG91_TEMPLATE_ID", ""),
                "mobile": phone_number,
                "message": message
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    result = await response.json()

                    if result.get("type") == "success":
                        return {
                            "status": True,
                            "message": "SMS sent successfully via MSG91",
                            "provider": "msg91",
                            "message_id": result.get("request_id")
                        }
                    else:
                        return {"status": False, "message": f"MSG91 error: {result.get('message', 'Unknown error')}"}

        except Exception as e:
            return {"status": False, "message": f"MSG91 failed: {str(e)}"}

    async def send_otp_sms(self, phone_number: str, otp: str, purpose: str = "login") -> Dict:
        """Send OTP SMS with formatted message"""
        message = f"Your MT5 Copy Trading {purpose.upper()} OTP is: {otp}. Valid for 5 minutes. Do not share this code. - 4xengineer.com"

        return await self.send_sms(phone_number, message)

    def get_provider_status(self) -> Dict:
        """Get current SMS provider status"""
        return {
            "active_provider": self.active_provider,
            "available_providers": list(self.providers.keys()),
            "configured": self.active_provider != "demo"
        }

# Create singleton instance
real_sms_service = RealSMSService()

# Configuration instructions for different providers
SMS_SETUP_INSTRUCTIONS = {
    "twilio": {
        "env_vars": ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM_NUMBER"],
        "signup_url": "https://www.twilio.com/try-twilio",
        "description": "International SMS service, requires credit card"
    },
    "fast2sms": {
        "env_vars": ["FAST2SMS_API_KEY"],
        "signup_url": "https://www.fast2sms.com/",
        "description": "Indian SMS service, supports Indian numbers"
    },
    "textlocal": {
        "env_vars": ["TEXTLOCAL_API_KEY"],
        "signup_url": "https://www.textlocal.in/",
        "description": "UK/India SMS service"
    },
    "msg91": {
        "env_vars": ["MSG91_API_KEY", "MSG91_TEMPLATE_ID"],
        "signup_url": "https://msg91.com/",
        "description": "Global SMS service with template support"
    }
}