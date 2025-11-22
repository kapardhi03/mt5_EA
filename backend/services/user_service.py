# ===================================
# COMPLETE services/user_service.py with missing update_user method
# ===================================
from datetime import datetime, timedelta
from bson import ObjectId
from backend.utils.mongo import insert_document, fetch_documents, update_document
from backend.services.mongodb_service import mongodb_service
from backend.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from backend.core.config import settings
from backend.services.otp_service import OTPService
import uuid

class UserService:
    def __init__(self):
        self.otp_service = OTPService()
    
    def clean_user_data(self, user_data: dict) -> dict:
        """Clean user data for API response"""
        # Remove sensitive fields
        cleaned_data = user_data.copy()
        cleaned_data.pop("password", None)
        
        # Ensure _id is string if present
        if "_id" in cleaned_data:
            cleaned_data["_id"] = str(cleaned_data["_id"])
            
        return cleaned_data
    
    async def register_user(self, user_data: dict) -> dict:
        """Register a new user"""
        # Check if user already exists
        existing_user = fetch_documents(
            settings.DATABASE_NAME, 
            "users", 
            {"$or": [{"email": user_data["email"]}, {"mobile": user_data["mobile"]}]}
        )
        
        if existing_user["status"] and existing_user["data"]:
            return {"status": False, "message": "User with this email or mobile already exists"}
        
        # Hash password
        hashed_password = hash_password(user_data["password"])
        
        # Create user record
        user_record = {
            "user_id": str(uuid.uuid4()),
            "name": user_data["name"],
            "mobile": user_data["mobile"],
            "email": user_data["email"],
            "country": user_data["country"],
            "state": user_data["state"],
            "city": user_data["city"],
            "pin_code": user_data["pin_code"],
            "password": hashed_password,
            "role": "member",  # Default role
            "status": "pending",  # Pending verification
            "mobile_verified": False,
            "email_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert user
        result = insert_document(settings.DATABASE_NAME, "users", user_record)
        if result["status"]:
            # Clean and return user data
            clean_user = self.clean_user_data(user_record)
            return {"status": True, "message": "User registered successfully", "data": clean_user}
        else:
            return {"status": False, "message": "Failed to register user", "error": result["error"]}
    
    async def login_user(self, mobile_or_email: str, password: str) -> dict:
        """Login user"""
        # Find user
        user_result = fetch_documents(
            settings.DATABASE_NAME,
            "users",
            {"$or": [{"email": mobile_or_email}, {"mobile": mobile_or_email}]}
        )
        
        if not user_result["status"] or not user_result["data"]:
            return {"status": False, "message": "Invalid credentials"}
        
        user = user_result["data"][0]
        
        # Verify password
        if not verify_password(password, user["password"]):
            return {"status": False, "message": "Invalid credentials"}
        
        # Check if user is active
        if user["status"] != "active":
            return {"status": False, "message": "Account is not active. Please verify your account."}
        
        # Generate tokens
        access_token = create_access_token(user["user_id"])
        refresh_token = create_refresh_token(user["user_id"])
        
        # Clean user data
        clean_user = self.clean_user_data(user)
        
        return {
            "status": True,
            "message": "Login successful",
            "data": {
                "user": clean_user,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        }
    
    async def get_user_by_id(self, user_id: str) -> dict:
        """Get user by ID"""
        # Try to find by legacy 'user_id' field first (UUID style)
        try:
            result = fetch_documents(settings.DATABASE_NAME, "users", {"user_id": user_id}, limit=1)
            if result["status"] and result["data"]:
                user = result["data"][0]
                clean_user = self.clean_user_data(user)
                return {"status": True, "data": clean_user}

            # If not found, try MongoDB ObjectId lookup
            try:
                oid = ObjectId(user_id)
                result2 = fetch_documents(settings.DATABASE_NAME, "users", {"_id": oid}, limit=1)
                if result2["status"] and result2["data"]:
                    user = result2["data"][0]
                    clean_user = self.clean_user_data(user)
                    return {"status": True, "data": clean_user}
            except Exception:
                # not a valid ObjectId or lookup failed
                pass

            return {"status": False, "message": "User not found"}
        except Exception as e:
            return {"status": False, "message": f"Error fetching user: {str(e)}"}
    
    # ===== MISSING METHOD - ADDED =====
    async def update_user(self, user_id: str, update_data: dict, updated_by: str) -> dict:
        """Update user profile/details"""
        try:
            # Verify user exists
            # Use mongodb_service to locate the user (handles legacy user_id and ObjectId)
            user_result = await mongodb_service.get_user_by_id(user_id)
            if not user_result or not user_result.get('status'):
                return {"status": False, "message": "User not found"}

            # Get the Mongo _id string from mongodb_service result
            mongo_id = user_result['data'].get('id') or user_result['data'].get('_id')
            if not mongo_id:
                return {"status": False, "message": "User identifier missing"}
            
            # Remove sensitive fields that shouldn't be updated via this method
            forbidden_fields = ["user_id", "password", "password_hash", "role", "created_at"]
            for field in forbidden_fields:
                update_data.pop(field, None)
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()

            # Perform async update via motor using mongodb_service's db
            db = mongodb_service.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            try:
                result = await db.users.update_one({"_id": ObjectId(mongo_id)}, {"$set": update_data})
            except Exception as e:
                return {"status": False, "message": f"Failed to update user: {str(e)}"}

            if result.modified_count > 0:
                updated_user = await mongodb_service.get_user_by_id(user_id)
                return {"status": True, "message": "User updated successfully", "data": updated_user.get('data')}
            else:
                # No modified count could mean data was identical; return success with current data
                current_user = await mongodb_service.get_user_by_id(user_id)
                return {"status": True, "message": "No changes applied (data may be identical)", "data": current_user.get('data')}
                
        except Exception as e:
            return {"status": False, "message": "Update failed", "error": str(e)}
    
    async def update_verification_status(self, user_id: str, verification_type: str, status: bool) -> dict:
        """Update user verification status (mobile_verified or email_verified)"""
        try:
            if verification_type not in ["mobile_verified", "email_verified"]:
                return {"status": False, "message": "Invalid verification type"}
            
            update_data = {verification_type: status}
            
            # If both verifications are complete, activate the account
            user_result = await self.get_user_by_id(user_id)
            if user_result["status"]:
                user = user_result["data"]
                # Check if this update completes verification
                if verification_type == "mobile_verified" and user.get("email_verified", False):
                    update_data["status"] = "active"
                elif verification_type == "email_verified" and user.get("mobile_verified", False):
                    update_data["status"] = "active"
            
            result = await self.update_user(user_id, update_data, "system")
            return result
            
        except Exception as e:
            return {"status": False, "message": "Verification update failed", "error": str(e)}
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> dict:
        """Change user password with current password verification"""
        try:
            # Get user with password for verification
            user_with_password = fetch_documents(
                settings.DATABASE_NAME, 
                "users", 
                {"user_id": user_id}
            )
            
            if not user_with_password["status"] or not user_with_password["data"]:
                return {"status": False, "message": "User not found"}
            
            user = user_with_password["data"][0]
            
            # Verify current password
            if not verify_password(current_password, user["password"]):
                return {"status": False, "message": "Current password is incorrect"}
            
            # Hash new password
            new_hashed_password = hash_password(new_password)
            
            # Update password
            result = update_document(
                settings.DATABASE_NAME,
                "users",
                "user_id",
                user_id,
                {"password": new_hashed_password, "updated_at": datetime.utcnow()}
            )
            
            if result["status"]:
                return {"status": True, "message": "Password changed successfully"}
            else:
                return {"status": False, "message": "Failed to change password"}
                
        except Exception as e:
            return {"status": False, "message": "Password change failed", "error": str(e)}

# Initialize service
user_service = UserService()