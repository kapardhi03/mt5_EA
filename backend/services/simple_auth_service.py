"""
Simple authentication service for immediate deployment
This service works with in-memory data and will be enhanced later
"""
import hashlib
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional

class SimpleAuthService:
    def __init__(self):
        self.users = {}
        self.tokens = {}
        self.otps = {}

        # Pre-create demo users
        self._create_demo_users()

    def _create_demo_users(self):
        """Create demo users for testing"""
        demo_users = [
            {
                "id": "user_001",
                "name": "Demo User",
                "email": "user@test.com",
                "mobile": "+1234567890",
                "password": "user123",
                "role": "user",
                "status": "active",
                "mobile_verified": True,
                "email_verified": True,
                "created_at": datetime.now()
            },
            {
                "id": "admin_001",
                "name": "Admin User",
                "email": "admin@test.com",
                "mobile": "+1234567891",
                "password": "admin123",
                "role": "admin",
                "status": "active",
                "mobile_verified": True,
                "email_verified": True,
                "created_at": datetime.now()
            },
            {
                "id": "master_001",
                "name": "Master Trader",
                "email": "master@test.com",
                "mobile": "+1234567892",
                "password": "master123",
                "role": "master",
                "status": "active",
                "mobile_verified": True,
                "email_verified": True,
                "created_at": datetime.now()
            }
        ]

        for user in demo_users:
            # Hash password
            user["password"] = self._hash_password(user["password"])
            self.users[user["email"]] = user
            self.users[user["mobile"]] = user

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return self._hash_password(plain_password) == hashed_password

    def _generate_token(self, user_id: str) -> str:
        """Generate access token"""
        token = secrets.token_urlsafe(32)
        self.tokens[token] = {
            "user_id": user_id,
            "expires_at": datetime.now() + timedelta(hours=24)
        }
        return token

    def _generate_otp(self) -> str:
        """Generate 6-digit OTP"""
        return str(secrets.randbelow(900000) + 100000)

    async def login_user(self, mobile_or_email: str, password: str) -> Dict:
        """Login user"""
        try:
            user = self.users.get(mobile_or_email)
            if not user:
                return {"status": False, "message": "User not found"}

            if not self._verify_password(password, user["password"]):
                return {"status": False, "message": "Invalid credentials"}

            if user["status"] != "active":
                return {"status": False, "message": "Account is not active"}

            # Generate token
            token = self._generate_token(user["id"])

            return {
                "status": True,
                "message": "Login successful",
                "data": {
                    "access_token": token,
                    "token_type": "bearer",
                    "user": {
                        "id": user["id"],
                        "name": user["name"],
                        "email": user["email"],
                        "mobile": user["mobile"],
                        "role": user["role"],
                        "status": user["status"]
                    }
                }
            }
        except Exception as e:
            return {"status": False, "message": f"Login error: {str(e)}"}

    async def send_otp(self, mobile_or_email: str, otp_type: str) -> Dict:
        """Send OTP"""
        try:
            otp = self._generate_otp()

            # Store OTP with 5-minute expiry
            self.otps[mobile_or_email] = {
                "otp": otp,
                "type": otp_type,
                "expires_at": datetime.now() + timedelta(minutes=5),
                "attempts": 0
            }

            # In demo mode, just return success with OTP in message
            return {
                "status": True,
                "message": f"OTP sent successfully. Demo OTP: {otp}",
                "data": {"otp": otp}  # Only for demo
            }
        except Exception as e:
            return {"status": False, "message": f"Failed to send OTP: {str(e)}"}

    async def verify_otp(self, mobile_or_email: str, otp: str, otp_type: str) -> Dict:
        """Verify OTP"""
        try:
            stored_otp = self.otps.get(mobile_or_email)
            if not stored_otp:
                return {"status": False, "message": "OTP not found or expired"}

            if datetime.now() > stored_otp["expires_at"]:
                del self.otps[mobile_or_email]
                return {"status": False, "message": "OTP has expired"}

            stored_otp["attempts"] += 1
            if stored_otp["attempts"] > 3:
                del self.otps[mobile_or_email]
                return {"status": False, "message": "Too many attempts. Please request new OTP"}

            if stored_otp["otp"] != otp:
                return {"status": False, "message": f"Invalid OTP. {3 - stored_otp['attempts']} attempts remaining"}

            # OTP verified successfully
            del self.otps[mobile_or_email]

            # Update user verification status
            user = self.users.get(mobile_or_email)
            if user:
                if otp_type == "mobile":
                    user["mobile_verified"] = True
                else:
                    user["email_verified"] = True

            return {"status": True, "message": "OTP verified successfully"}
        except Exception as e:
            return {"status": False, "message": f"OTP verification error: {str(e)}"}

    async def register_user(self, user_data: Dict) -> Dict:
        """Register new user"""
        try:
            email = user_data["email"]
            mobile = user_data["mobile"]

            # Check if user already exists
            if email in self.users or mobile in self.users:
                return {"status": False, "message": "User already exists"}

            # Create new user
            user_id = f"user_{len(self.users) + 1:03d}"
            user = {
                "id": user_id,
                "name": user_data["name"],
                "email": email,
                "mobile": mobile,
                "password": self._hash_password(user_data["password"]),
                "country": user_data["country"],
                "state": user_data["state"],
                "city": user_data["city"],
                "pin_code": user_data["pin_code"],
                "role": "user",  # Default role
                "status": "active",
                "mobile_verified": False,
                "email_verified": False,
                "created_at": datetime.now()
            }

            self.users[email] = user
            self.users[mobile] = user

            return {
                "status": True,
                "message": "User registered successfully",
                "data": {"user_id": user_id}
            }
        except Exception as e:
            return {"status": False, "message": f"Registration error: {str(e)}"}

    async def get_user_by_token(self, token: str) -> Optional[Dict]:
        """Get user by token"""
        token_data = self.tokens.get(token)
        if not token_data:
            return None

        if datetime.now() > token_data["expires_at"]:
            del self.tokens[token]
            return None

        # Find user by ID
        for user in self.users.values():
            if user["id"] == token_data["user_id"]:
                return user

        return None

# Create singleton instance
simple_auth_service = SimpleAuthService()