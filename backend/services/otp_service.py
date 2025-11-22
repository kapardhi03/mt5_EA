# ===================================
# services/otp_service.py
# ===================================
import random
import secrets
from datetime import datetime, timedelta
from typing import Dict
from backend.core.config import settings
from backend.services.real_sms_service import real_sms_service
from backend.services.email_service import email_service
from backend.services.mongodb_service import mongodb_service

# Optional Twilio import
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    Client = None

class OTPService:
    def __init__(self):
        self.twilio_client = None
        if TWILIO_AVAILABLE and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    def generate_otp(self) -> str:
        """Generate random OTP"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(settings.OTP_LENGTH)])
    
    async def send_mobile_otp(self, mobile: str, purpose: str = "verification") -> Dict:
        """Send OTP via SMS using real SMS service"""
        try:
            # Store OTP in database using MongoDB service (this generates the OTP)
            otp_result = await mongodb_service.send_otp(mobile, "mobile", purpose)
            
            if not otp_result["status"]:
                return {"status": False, "message": "Failed to generate OTP"}
            
            # Get the OTP from the database result
            otp = otp_result["data"]["otp"]
            
            # Send SMS using real SMS service
            sms_result = await real_sms_service.send_otp_sms(mobile, otp, purpose)
            
            if sms_result["status"]:
                return {
                    "status": True, 
                    "message": "OTP sent successfully",
                    "data": {"otp": otp} if real_sms_service.active_provider == "demo" else None
                }
            else:
                return {
                    "status": True,  # OTP generated and stored, SMS might have failed
                    "message": f"OTP generated but SMS failed: {sms_result['message']}",
                    "data": {"otp": otp, "sms_error": sms_result["message"]}
                }
                
        except Exception as e:
            return {"status": False, "message": f"Error sending mobile OTP: {str(e)}"}
    
    async def send_email_otp(self, email: str, purpose: str = "verification") -> Dict:
        """Send OTP via Email using email service"""
        try:
            # Store OTP in database using MongoDB service (this generates the OTP)
            otp_result = await mongodb_service.send_otp(email, "email", purpose)
            
            if not otp_result["status"]:
                return {"status": False, "message": "Failed to generate OTP"}
            
            # Get the OTP from the database result
            otp = otp_result["data"]["otp"]
            
            # Send email using email service
            email_result = await email_service.send_otp_email(email, otp, purpose)
            
            if email_result["status"]:
                return {
                    "status": True, 
                    "message": "OTP sent successfully",
                    "data": {"otp": otp}  # For demo mode
                }
            else:
                return {
                    "status": True,  # OTP generated and stored, email might have failed
                    "message": f"OTP generated but email failed: {email_result['message']}",
                    "data": {"otp": otp, "email_error": email_result["message"]}
                }
                
        except Exception as e:
            return {"status": False, "message": f"Error sending email OTP: {str(e)}"}
    
    async def verify_otp(self, identifier: str, otp: str, otp_type: str) -> Dict:
        """Verify OTP using MongoDB service"""
        try:
            return await mongodb_service.verify_otp(identifier, otp, otp_type)
        except Exception as e:
            return {"status": False, "message": f"Error verifying OTP: {str(e)}"}
    
    async def send_otp(self, mobile_or_email: str, otp_type: str, purpose: str = "verification") -> Dict:
        """Send OTP based on type"""
        if otp_type == "mobile":
            return await self.send_mobile_otp(mobile_or_email, purpose)
        elif otp_type == "email":
            return await self.send_email_otp(mobile_or_email, purpose)
        else:
            return {"status": False, "message": "Invalid OTP type"}

# Create singleton instance
otp_service = OTPService()