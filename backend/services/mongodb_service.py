"""
MongoDB service for MT5 Copy Trading Platform
Handles all database operations with real MongoDB Atlas
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from backend.core.database import get_database
from backend.models.database_models import *

class MongoDBService:
    def __init__(self):
        self.db = None

    def get_db(self):
        if self.db is None:
            self.db = get_database()
        return self.db

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return self._hash_password(plain_password) == hashed_password

    def _generate_api_key(self) -> str:
        """Generate API key for groups"""
        return f"mt5_api_{secrets.token_urlsafe(32)}"

    def _generate_otp(self) -> str:
        """Generate 6-digit OTP"""
        return str(secrets.randbelow(900000) + 100000)

    # ===================================
    # Temporary User Management (Registration Flow)
    # ===================================

    async def create_temp_user(self, user_data: Dict) -> Dict:
        """Create temporary user during registration"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Hash password
            user_data["password_hash"] = self._hash_password(user_data["password"])
            del user_data["password"]

            # Insert temp user
            result = await db.temp_users.insert_one(user_data)

            return {
                "status": True,
                "message": "Temporary user created successfully",
                "data": {"temp_user_id": str(result.inserted_id)}
            }

        except Exception as e:
            return {"status": False, "message": f"Error creating temp user: {str(e)}"}

    async def get_temp_user_by_token(self, registration_token: str) -> Dict:
        """Get temporary user by registration token"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            temp_user = await db.temp_users.find_one({
                "registration_token": registration_token,
                "registration_expires": {"$gt": datetime.now()}
            })

            if temp_user:
                temp_user["_id"] = str(temp_user["_id"])
                return {"status": True, "data": temp_user}
            else:
                return {"status": False, "message": "Temp user not found or expired"}

        except Exception as e:
            return {"status": False, "message": f"Error fetching temp user: {str(e)}"}

    async def update_temp_user(self, registration_token: str, update_data: Dict) -> Dict:
        """Update temporary user data"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            result = await db.temp_users.update_one(
                {"registration_token": registration_token},
                {"$set": update_data}
            )

            if result.modified_count > 0:
                return {"status": True, "message": "Temp user updated successfully"}
            else:
                return {"status": False, "message": "Temp user not found"}

        except Exception as e:
            return {"status": False, "message": f"Error updating temp user: {str(e)}"}

    async def delete_temp_user(self, registration_token: str) -> Dict:
        """Delete temporary user after successful registration"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            result = await db.temp_users.delete_one({"registration_token": registration_token})

            if result.deleted_count > 0:
                return {"status": True, "message": "Temp user deleted successfully"}
            else:
                return {"status": False, "message": "Temp user not found"}

        except Exception as e:
            return {"status": False, "message": f"Error deleting temp user: {str(e)}"}

    async def get_available_trading_groups(self) -> Dict:
        """Get list of available trading groups for registration"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            groups_cursor = db.trading_groups.find(
                {"trading_status": "active"},
                {
                    "group_name": 1,
                    "company_name": 1,
                    "description": 1,
                    "profit_sharing_percentage": 1,
                    "settlement_cycle": 1,
                    "active_members": 1
                }
            )
            groups = await groups_cursor.to_list(length=None)

            for group in groups:
                group["_id"] = str(group["_id"])

            return {
                "status": True,
                "data": {"groups": groups}
            }

        except Exception as e:
            return {"status": False, "message": f"Error fetching groups: {str(e)}"}

    # ===================================
    # User Management
    # ===================================

    async def create_user(self, user_data: Dict) -> Dict:
        """Create new user in database"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Check if user already exists
            existing_user = await db.users.find_one({
                "$or": [
                    {"email": user_data["email"]},
                    {"mobile": user_data["mobile"]}
                ]
            })

            if existing_user:
                return {"status": False, "message": "User with this email or mobile already exists"}

            # Create complete user document with all registration fields
            user_document = {
                "name": user_data["name"],
                "mobile": user_data["mobile"],
                "email": user_data["email"],
                "country": user_data["country"],
                "state": user_data["state"],
                "city": user_data["city"],
                "pin_code": user_data["pin_code"],
                "password_hash": self._hash_password(user_data["password"]),
                "role": user_data.get("role", "user"),
                "status": "pending",
                "mobile_verified": False,
                "email_verified": False,

                # Broker and account details from registration
                "broker": user_data.get("broker"),
                "account_no": user_data.get("account_no"),
                "trading_password_hash": self._hash_password(user_data.get("trading_password", "")),

                # IB workflow - set to pending until admin approval
                "ib_status": "pending",
                "ib_proof_filename": None,
                "ib_proof_upload_date": None,
                "ib_approval_date": None,
                "ib_approved_by": None,
                "ib_rejection_reason": None,

                # Group membership
                "group_id": None,
                "group_join_date": None,
                "referral_code_used": user_data.get("referral_code"),

                # Timestamps
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "last_login": None,
                "login_attempts": 0,
                "locked_until": None
            }

            # Insert user
            result = await db.users.insert_one(user_document)
            user_id = str(result.inserted_id)

            print(f"✅ User created successfully with ID: {user_id}")

            return {
                "status": True,
                "message": "User created successfully",
                "data": {
                    "user_id": user_id,
                    "status": "pending",
                    "message": "Account created. Please wait for admin approval."
                }
            }

        except Exception as e:
            print(f"❌ Error creating user: {str(e)}")
            return {"status": False, "message": f"Error creating user: {str(e)}"}

    async def _handle_group_join_by_referral(self, user_id: str, referral_code: str) -> Dict:
        """Handle group joining by referral code"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Find group by API key or referral code
            group = await db.groups.find_one({
                "$or": [
                    {"api_key": referral_code},
                    {"referral_code": referral_code}
                ]
            })

            if group:
                # Update user with group membership
                await db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {
                        "group_id": str(group["_id"]),
                        "group_join_date": datetime.now(),
                        "referral_code_used": referral_code
                    }}
                )
                print(f"✅ User {user_id} joined group {group['group_name']}")
                return {"status": True, "message": "Joined group successfully"}
            else:
                print(f"⚠️ Referral code {referral_code} not found")
                return {"status": False, "message": "Invalid referral code"}

        except Exception as e:
            print(f"❌ Error handling group join: {str(e)}")
            return {"status": False, "message": f"Error joining group: {str(e)}"}

    async def authenticate_user(self, mobile_or_email: str, password: str) -> Dict:
        """Authenticate user with database"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Find user by email or mobile
            user = await db.users.find_one({
                "$or": [
                    {"email": mobile_or_email},
                    {"mobile": mobile_or_email}
                ]
            })

            if not user:
                return {"status": False, "message": "User not found"}

            # Verify password
            if not self._verify_password(password, user["password_hash"]):
                return {"status": False, "message": "Invalid credentials"}

            # Ensure account is active
            if user.get("status") != "active":
                return {"status": False, "message": "Account is not active"}

            # Temporarily bypass IB approval for all roles: business asked to allow
            # logins regardless of IB workflow status so we skip the check entirely.

            # Update last login
            await db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"last_login": datetime.now()}}
            )

            # Return user data
            user_data = {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"],
                "mobile": user["mobile"],
                "role": user["role"],
                "status": user["status"]
            }

            return {
                "status": True,
                "message": "Authentication successful",
                "data": user_data
            }

        except Exception as e:
            return {"status": False, "message": f"Authentication error: {str(e)}"}

    async def get_user_by_id(self, user_id: str) -> Dict:
        """Get user by ID"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            user = None
            # Try lookup by MongoDB _id (ObjectId)
            try:
                user = await db.users.find_one({"_id": ObjectId(user_id)})
            except Exception:
                user = None

            # If not found, try lookup by legacy 'user_id' field (some parts of system use uuid)
            if not user:
                user = await db.users.find_one({"user_id": user_id})

            if not user:
                return {"status": False, "message": "User not found"}

            user_data = {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"],
                "mobile": user["mobile"],
                "role": user["role"],
                "status": user["status"],
                "mobile_verified": user.get("mobile_verified", False),
                "email_verified": user.get("email_verified", False),
                "created_at": user["created_at"]
            }

            return {"status": True, "data": user_data}

        except Exception as e:
            return {"status": False, "message": f"Error fetching user: {str(e)}"}

    async def get_user_by_email(self, email: str) -> Dict:
        """Get user by email"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            user = await db.users.find_one({"email": email})
            if not user:
                return None

            user_data = {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"],
                "mobile": user["mobile"],
                "password": user.get("password_hash", user.get("password", "")),
                "role": user["role"],
                "status": user["status"],
                "mobile_verified": user.get("mobile_verified", False),
                "email_verified": user.get("email_verified", False),
                "created_at": user["created_at"]
            }

            return user_data

        except Exception as e:
            return None

    async def get_all_users(self) -> Dict:
        """Get all users from database"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            users_cursor = db.users.find({})
            users = await users_cursor.to_list(length=None)

            users_data = []
            for user in users:
                user_data = {
                    "_id": str(user["_id"]),
                    "id": str(user["_id"]),
                    "name": user["name"],
                    "email": user["email"],
                    "mobile": user["mobile"],
                    "role": user["role"],
                    "status": user["status"],
                    "country": user.get("country", ""),
                    "state": user.get("state", ""),
                    "city": user.get("city", ""),
                    "broker": user.get("broker", ""),
                    "account_no": user.get("account_no", ""),
                    "mobile_verified": user.get("mobile_verified", False),
                    "email_verified": user.get("email_verified", False),
                    "ib_status": user.get("ib_status", "not_changed"),
                    "group_id": user.get("group_id"),
                    "created_at": user.get("created_at"),
                    "last_login": user.get("last_login"),
                    "kyc_status": user.get("status", "pending")
                }
                users_data.append(user_data)

            return {"status": True, "data": users_data}
        except Exception as e:
            print(f"❌ Error getting all users: {str(e)}")
            return {"status": False, "message": f"Error: {str(e)}"}

    # ===================================
    # OTP Management
    # ===================================

    async def send_otp(self, mobile_or_email: str, otp_type: str, purpose: str = "login") -> Dict:
        """Generate and store OTP"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            otp_code = self._generate_otp()
            expires_at = datetime.now() + timedelta(minutes=5)

            # Store OTP in database
            otp_record = {
                "mobile_or_email": mobile_or_email,
                "otp_code": otp_code,
                "otp_type": otp_type,
                "purpose": purpose,
                "expires_at": expires_at,
                "status": "pending",
                "attempts": 0,
                "created_at": datetime.now()
            }

            # Remove any existing OTP for this mobile/email
            await db.otp_records.delete_many({"mobile_or_email": mobile_or_email})

            # Insert new OTP
            result = await db.otp_records.insert_one(otp_record)

            return {
                "status": True,
                "message": f"OTP sent successfully",
                "data": {"otp": otp_code}  # For demo mode
            }

        except Exception as e:
            return {"status": False, "message": f"Error sending OTP: {str(e)}"}

    async def verify_otp(self, mobile_or_email: str, otp_code: str, otp_type: str) -> Dict:
        """Verify OTP from database"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Find OTP record
            query = {
                "mobile_or_email": mobile_or_email,
                "otp_type": otp_type,
                "status": "pending"
            }
            
            otp_record = await db.otp_records.find_one(query)

            if not otp_record:
                return {"status": False, "message": "OTP not found or already used"}

            # Check expiry
            if datetime.now() > otp_record["expires_at"]:
                await db.otp_records.update_one(
                    {"_id": otp_record["_id"]},
                    {"$set": {"status": "expired"}}
                )
                return {"status": False, "message": "OTP has expired"}

            # Check attempts
            attempts = otp_record.get("attempts", 0)
            if attempts >= 3:
                await db.otp_records.update_one(
                    {"_id": otp_record["_id"]},
                    {"$set": {"status": "failed"}}
                )
                return {"status": False, "message": "Too many attempts. Please request new OTP"}

            # Increment attempts
            await db.otp_records.update_one(
                {"_id": otp_record["_id"]},
                {"$inc": {"attempts": 1}}
            )

            # Verify OTP
            if otp_record["otp_code"] != otp_code:
                attempts_left = 3 - (attempts + 1)
                return {"status": False, "message": f"Invalid OTP. {attempts_left} attempts remaining"}

            # OTP verified successfully
            await db.otp_records.update_one(
                {"_id": otp_record["_id"]},
                {
                    "$set": {
                        "status": "verified",
                        "verified_at": datetime.now()
                    }
                }
            )

            # Update user verification status
            update_field = "mobile_verified" if otp_type == "mobile" else "email_verified"
            # Update the user's verification flag
            await db.users.update_one(
                {
                    "$or": [
                        {"email": mobile_or_email},
                        {"mobile": mobile_or_email}
                    ]
                },
                {"$set": {update_field: True, "updated_at": datetime.now()}}
            )

            return {"status": True, "message": "OTP verified successfully"}

        except Exception as e:
            return {"status": False, "message": f"OTP verification error: {str(e)}"}

    # ===================================
    # Group Management
    # ===================================

    async def create_group(self, group_data: Dict, created_by: str) -> Dict:
        """Create new trading group"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Check if group name already exists
            existing_group = db.groups.find_one({"group_name": group_data["group_name"]})
            if existing_group:
                return {"status": False, "message": "Group name already exists"}

            # Generate API key
            api_key = self._generate_api_key()

            # Create group
            group = TradingGroup(
                group_name=group_data["group_name"],
                company_name=group_data["company_name"],
                profit_sharing_percentage=group_data["profit_sharing_percentage"],
                settlement_cycle=SettlementCycle(group_data["settlement_cycle"]),
                grace_days=group_data.get("grace_days", 2),
                api_key=api_key,
                created_by=created_by
            )

            result = db.groups.insert_one(group.dict(exclude={"id"}))
            group_id = str(result.inserted_id)

            return {
                "status": True,
                "message": "Group created successfully",
                "data": {
                    "group_id": group_id,
                    "api_key": api_key
                }
            }

        except Exception as e:
            return {"status": False, "message": f"Error creating group: {str(e)}"}

    async def get_groups(self, filters: Optional[Dict] = None) -> Dict:
        """Get all trading groups"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            query = filters or {}
            groups = list(db.groups.find(query))

            # Convert ObjectIds to strings
            for group in groups:
                group["id"] = str(group["_id"])
                del group["_id"]

            return {
                "status": True,
                "data": groups
            }

        except Exception as e:
            return {"status": False, "message": f"Error fetching groups: {str(e)}"}

    # ===================================
    # Member Management
    # ===================================

    async def add_member_to_group(self, member_data: Dict) -> Dict:
        """Add member to trading group"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Check if member already exists in group
            existing_member = db.members.find_one({
                "user_id": member_data["user_id"],
                "group_id": member_data["group_id"]
            })

            if existing_member:
                return {"status": False, "message": "Member already exists in this group"}

            # Create member record
            member = GroupMember(
                user_id=member_data["user_id"],
                group_id=member_data["group_id"],
                account_id=member_data["account_id"],
                opening_balance=member_data.get("opening_balance", 0.0),
                lot_multiplier=member_data.get("lot_multiplier", 1.0)
            )

            result = db.members.insert_one(member.dict(exclude={"id"}))
            member_id = str(result.inserted_id)

            # Update group member count
            db.groups.update_one(
                {"_id": ObjectId(member_data["group_id"])},
                {"$inc": {"total_members": 1}}
            )

            return {
                "status": True,
                "message": "Member added successfully",
                "data": {"member_id": member_id}
            }

        except Exception as e:
            return {"status": False, "message": f"Error adding member: {str(e)}"}

    # ===================================
    # Settlement Management
    # ===================================

    async def create_settlement(self, settlement_data: Dict) -> Dict:
        """Create settlement request"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            settlement = Settlement(**settlement_data)
            result = db.settlements.insert_one(settlement.dict(exclude={"id"}))
            settlement_id = str(result.inserted_id)

            return {
                "status": True,
                "message": "Settlement created successfully",
                "data": {"settlement_id": settlement_id}
            }

        except Exception as e:
            return {"status": False, "message": f"Error creating settlement: {str(e)}"}

    # ===================================
    # Trading Account Management
    # ===================================

    async def create_trading_account(self, account_data: Dict) -> Dict:
        """Create trading account"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Check if account already exists
            existing_account = db.trading_accounts.find_one({
                "account_number": account_data["account_number"],
                "broker": account_data["broker"]
            })

            if existing_account:
                return {"status": False, "message": "Trading account already exists"}

            account = TradingAccount(
                user_id=account_data["user_id"],
                account_number=account_data["account_number"],
                account_type=AccountType(account_data["account_type"]),
                broker=BrokerType(account_data["broker"]),
                server=account_data["server"],
                partner_id=account_data["partner_id"],
                password_hash=self._hash_password(account_data["password"]),
                currency=account_data.get("currency", "USD"),
                lot_multiplier=account_data.get("lot_multiplier", 1.0),
                is_cent_account=account_data.get("is_cent_account", False)
            )

            result = db.trading_accounts.insert_one(account.dict(exclude={"id"}))
            account_id = str(result.inserted_id)

            return {
                "status": True,
                "message": "Trading account created successfully",
                "data": {"account_id": account_id}
            }

        except Exception as e:
            return {"status": False, "message": f"Error creating trading account: {str(e)}"}

    # ===================================
    # Error Logging
    # ===================================

    async def log_error(self, error_data: Dict) -> Dict:
        """Log error to database"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            error_log = ErrorLog(**error_data)
            result = db.error_logs.insert_one(error_log.dict(exclude={"id"}))

            return {
                "status": True,
                "message": "Error logged successfully",
                "data": {"error_id": str(result.inserted_id)}
            }

        except Exception as e:
            return {"status": False, "message": f"Error logging failed: {str(e)}"}

    # ===================================
    # Initialization and Demo Data
    # ===================================

    async def initialize_demo_data(self) -> Dict:
        """Initialize demo data for testing"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Create demo users if they don't exist
            demo_users = [
                {
                    "name": "Demo User",
                    "email": "user@test.com",
                    "mobile": "+1234567890",
                    "password": "user123",
                    "country": "United States",
                    "state": "California",
                    "city": "Los Angeles",
                    "pin_code": "90210",
                    "role": "user",
                    "status": "active"
                },
                {
                    "name": "Admin User",
                    "email": "admin@test.com",
                    "mobile": "+1234567891",
                    "password": "admin123",
                    "country": "United States",
                    "state": "California",
                    "city": "Los Angeles",
                    "pin_code": "90210",
                    "role": "admin",
                    "status": "active"
                },
                {
                    "name": "Master Trader",
                    "email": "master@test.com",
                    "mobile": "+1234567892",
                    "password": "master123",
                    "country": "United States",
                    "state": "California",
                    "city": "Los Angeles",
                    "pin_code": "90210",
                    "role": "master",
                    "status": "active"
                }
            ]

            created_users = []
            for user_data in demo_users:
                # Check if user exists
                existing_user = db.users.find_one({"email": user_data["email"]})
                if not existing_user:
                    user = User(
                        name=user_data["name"],
                        mobile=user_data["mobile"],
                        email=user_data["email"],
                        country=user_data["country"],
                        state=user_data["state"],
                        city=user_data["city"],
                        pin_code=user_data["pin_code"],
                        password_hash=self._hash_password(user_data["password"]),
                        role=UserRole(user_data["role"]),
                        status=UserStatus(user_data["status"]),
                        mobile_verified=True,
                        email_verified=True
                    )
                    result = db.users.insert_one(user.dict(exclude={"id"}))
                    created_users.append(str(result.inserted_id))

            return {
                "status": True,
                "message": f"Demo data initialized. Created {len(created_users)} users.",
                "data": {"created_users": created_users}
            }

        except Exception as e:
            return {"status": False, "message": f"Error initializing demo data: {str(e)}"}

    # ===================================
    # Admin Functions
    # ===================================

    async def get_all_users(self, filters: Dict = None) -> Dict:
        """Get all users with optional filters (admin only)"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            query = filters or {}

            # Get all users
            cursor = db.users.find(query).sort("created_at", -1)
            users = await cursor.to_list(length=None)

            user_list = []
            for user in users:
                user_data = {
                    "id": str(user["_id"]),
                    "name": user["name"],
                    "email": user["email"],
                    "mobile": user["mobile"],
                    "role": user["role"],
                    "status": user["status"],
                    "mobile_verified": user.get("mobile_verified", False),
                    "email_verified": user.get("email_verified", False),
                    "created_at": user["created_at"],
                    "last_login": user.get("last_login")
                }
                user_list.append(user_data)

            return {"status": True, "data": user_list}

        except Exception as e:
            return {"status": False, "message": f"Error fetching users: {str(e)}"}

    async def update_user_status(self, user_id: str, new_status: str) -> Dict:
        """Update user status (admin only)"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            result = await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"status": new_status, "updated_at": datetime.now()}}
            )

            if result.modified_count > 0:
                return {"status": True, "message": f"User status updated to {new_status}"}
            else:
                return {"status": False, "message": "User not found or status not changed"}

        except Exception as e:
            return {"status": False, "message": f"Error updating user status: {str(e)}"}

    async def update_user_role(self, user_id: str, new_role: str) -> Dict:
        """Update user role (admin only)"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            result = await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"role": new_role, "updated_at": datetime.now()}}
            )

            if result.modified_count > 0:
                return {"status": True, "message": f"User role updated to {new_role}"}
            else:
                return {"status": False, "message": "User not found or role not changed"}

        except Exception as e:
            return {"status": False, "message": f"Error updating user role: {str(e)}"}

    async def update_user_status_by_email(self, email: str, new_status: str) -> Dict:
        """Update user status by email (admin only)"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # First check if user exists
            user_check = await db.users.find_one({"email": email})
            if not user_check:
                return {"status": False, "message": f"User with email {email} not found"}

            print(f"🔍 Found user: {user_check.get('name', 'Unknown')} with current status: {user_check.get('status', 'Unknown')}")

            result = await db.users.update_one(
                {"email": email},
                {"$set": {"status": new_status, "updated_at": datetime.now()}}
            )

            print(f"📝 Update result - Modified count: {result.modified_count}")

            if result.modified_count > 0:
                return {"status": True, "message": f"User status updated to {new_status}"}
            else:
                return {"status": False, "message": "User found but status not changed (might already be the same)"}

        except Exception as e:
            print(f"💥 Error in update_user_status_by_email: {str(e)}")
            return {"status": False, "message": f"Error updating user status: {str(e)}"}

    async def delete_user_permanently(self, user_id: str) -> Dict:
        """Delete a suspended user and related records"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            user_lookup = await self.get_user_by_id(user_id)
            if not user_lookup.get("status"):
                return {"status": False, "message": "User not found"}

            user_data = user_lookup.get("data", {})
            user_status = (user_data.get("status") or "").lower()
            if user_status not in ("suspended", "inactive"):
                return {"status": False, "message": "Only suspended users can be deleted"}

            mongo_id = user_data.get("id")
            if not mongo_id:
                return {"status": False, "message": "User identifier missing"}

            identifiers = {user_id, mongo_id}
            identifiers = {str(value) for value in identifiers if value}

            object_identifiers = []
            try:
                object_identifiers.append(ObjectId(mongo_id))
            except Exception:
                pass

            member_conditions = []
            if identifiers:
                member_conditions.append({"user_id": {"$in": list(identifiers)}})
            if object_identifiers:
                member_conditions.append({"user_id": {"$in": object_identifiers}})

            account_conditions = []
            if identifiers:
                account_conditions.append({"user_id": {"$in": list(identifiers)}})
            if object_identifiers:
                account_conditions.append({"user_id": {"$in": object_identifiers}})

            member_deleted = 0
            if member_conditions:
                member_deleted = (await db.members.delete_many({"$or": member_conditions})).deleted_count

            account_deleted = 0
            if account_conditions:
                account_deleted = (await db.trading_accounts.delete_many({"$or": account_conditions})).deleted_count

            # Finally delete user document
            delete_result = await db.users.delete_one({"_id": ObjectId(mongo_id)})
            if delete_result.deleted_count == 0:
                return {"status": False, "message": "Failed to delete user document"}

            return {
                "status": True,
                "message": "User deleted successfully",
                "data": {
                    "deleted_user_id": mongo_id,
                    "related_records_removed": {
                        "members": member_deleted,
                        "trading_accounts": account_deleted
                    }
                }
            }

        except Exception as e:
            return {"status": False, "message": f"Error deleting user: {str(e)}"}

    async def update_user_details(self, user_id: str, updates: Dict[str, Any]) -> Dict:
        """Allow admin to update user profile fields"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            user_lookup = await self.get_user_by_id(user_id)
            if not user_lookup.get("status"):
                return {"status": False, "message": "User not found"}

            mongo_id = user_lookup.get("data", {}).get("id")
            if not mongo_id:
                return {"status": False, "message": "User identifier missing"}

            allowed_fields = {
                "name", "email", "mobile", "country", "state", "city",
                "pin_code", "kyc_status", "status"
            }
            payload = {key: value for key, value in updates.items() if key in allowed_fields}

            if not payload:
                return {"status": False, "message": "No editable fields supplied"}

            payload["updated_at"] = datetime.now()

            result = await db.users.update_one({"_id": ObjectId(mongo_id)}, {"$set": payload})
            if result.modified_count == 0:
                return {"status": False, "message": "No changes applied"}

            refreshed = await self.get_user_by_id(user_id)
            return {"status": True, "message": "User updated successfully", "data": refreshed.get("data")}

        except Exception as e:
            return {"status": False, "message": f"Error updating user: {str(e)}"}

    async def activate_user_by_email(self, email: str) -> Dict:
        """Activate user by email (admin only)"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            result = await db.users.update_one(
                {"email": email},
                {"$set": {"status": "active", "updated_at": datetime.now()}}
            )

            if result.modified_count > 0:
                return {"status": True, "message": f"User {email} activated successfully"}
            else:
                return {"status": False, "message": "User not found"}

        except Exception as e:
            return {"status": False, "message": f"Error activating user: {str(e)}"}

    async def get_pending_members(self) -> Dict:
        """Get all pending member approvals"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Get users with pending status
            cursor = db.users.find({"status": "pending"}).sort("created_at", -1)
            pending_users = await cursor.to_list(length=None)

            members_list = []
            for user in pending_users:
                member_data = {
                    "member_id": str(user["_id"]),
                    "user_name": user["name"],
                    "user_mobile": user["mobile"],
                    "user_email": user["email"],
                    "account_number": user.get("mobile", "")[-4:],  # Mock account number
                    "account_type": "Standard",
                    "balance": 0.0,
                    "lot_multiplier": 1,
                    "current_balance": 0.0,
                    "created_at": user["created_at"],
                    "status": user["status"]
                }
                members_list.append(member_data)

            return {"status": True, "data": {"members": members_list}}

        except Exception as e:
            return {"status": False, "message": f"Error fetching pending members: {str(e)}"}

    async def approve_member(self, member_id: str) -> Dict:
        """Approve a pending member"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            result = await db.users.update_one(
                {"_id": ObjectId(member_id)},
                {"$set": {"status": "active", "approved_at": datetime.now()}}
            )

            if result.modified_count > 0:
                return {"status": True, "message": "Member approved successfully"}
            else:
                return {"status": False, "message": "Member not found"}

        except Exception as e:
            return {"status": False, "message": f"Error approving member: {str(e)}"}

    async def reject_member(self, member_id: str, reason: Dict) -> Dict:
        """Reject a pending member"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            result = await db.users.update_one(
                {"_id": ObjectId(member_id)},
                {"$set": {
                    "status": "rejected",
                    "rejected_at": datetime.now(),
                    "rejection_reason": reason.get("reason", "No reason provided")
                }}
            )

            if result.modified_count > 0:
                return {"status": True, "message": "Member rejected successfully"}
            else:
                return {"status": False, "message": "Member not found"}

        except Exception as e:
            return {"status": False, "message": f"Error rejecting member: {str(e)}"}

    async def get_groups(self, filters: Dict = None) -> Dict:
        """Get all groups (admin view)"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Mock groups data for now
            groups = [
                {
                    "id": "group_001",
                    "group_name": "Alpha Trading Group",
                    "company_name": "Alpha Trading Co.",
                    "settlement_cycle": "weekly",
                    "active_members": 15,
                    "total_members": 18,
                    "total_equity": 125000.0,
                    "total_profit": 8500.0,
                    "pending_settlement": 1200.0,
                    "next_settlement_date": "2025-09-22",
                    "trading_status": "active",
                    "api_key": "mt5_api_abc123xyz789def456",
                    "created_at": datetime.now()
                },
                {
                    "id": "group_002",
                    "group_name": "Beta Forex Masters",
                    "company_name": "Beta Forex Ltd.",
                    "settlement_cycle": "monthly",
                    "active_members": 22,
                    "total_members": 25,
                    "total_equity": 185000.0,
                    "total_profit": 12300.0,
                    "pending_settlement": 2100.0,
                    "next_settlement_date": "2025-10-01",
                    "trading_status": "active",
                    "api_key": "mt5_api_def456ghi789jkl012",
                    "created_at": datetime.now()
                }
            ]

            return {"status": True, "data": {"groups": groups}}

        except Exception as e:
            return {"status": False, "message": f"Error fetching groups: {str(e)}"}

    async def update_group_status(self, group_id: str, status_data: Dict) -> Dict:
        """Update group status"""
        try:
            # Mock implementation for now
            return {
                "status": True,
                "message": f"Group status updated to {status_data.get('status', 'unknown')}"
            }

        except Exception as e:
            return {"status": False, "message": f"Error updating group status: {str(e)}"}

    async def create_password_reset_token(self, email: str) -> Dict:
        """Create password reset token for user"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Check if user exists
            user = await db.users.find_one({"email": email})
            if not user:
                return {"status": False, "message": "User not found"}

            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=24)

            # Store reset token
            reset_record = {
                "email": email,
                "reset_token": reset_token,
                "expires_at": expires_at,
                "used": False,
                "created_at": datetime.now()
            }

            # Remove any existing reset tokens for this email
            await db.password_resets.delete_many({"email": email})

            # Insert new reset token
            await db.password_resets.insert_one(reset_record)

            return {
                "status": True,
                "message": "Password reset token created successfully",
                "data": {"reset_token": reset_token}
            }

        except Exception as e:
            return {"status": False, "message": f"Error creating password reset token: {str(e)}"}

    async def reset_password_with_token(self, email: str, reset_token: str, new_password: str) -> Dict:
        """Reset password using reset token"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Find reset token
            reset_record = await db.password_resets.find_one({
                "email": email,
                "reset_token": reset_token,
                "used": False
            })

            if not reset_record:
                return {"status": False, "message": "Invalid or expired reset token"}

            if datetime.now() > reset_record["expires_at"]:
                return {"status": False, "message": "Reset token has expired"}

            # Update user password
            result = await db.users.update_one(
                {"email": email},
                {"$set": {
                    "password_hash": self._hash_password(new_password),
                    "updated_at": datetime.now()
                }}
            )

            if result.modified_count > 0:
                # Mark token as used
                await db.password_resets.update_one(
                    {"_id": reset_record["_id"]},
                    {"$set": {"used": True}}
                )

                return {"status": True, "message": "Password reset successfully"}
            else:
                return {"status": False, "message": "Failed to update password"}

        except Exception as e:
            return {"status": False, "message": f"Error resetting password: {str(e)}"}

    async def admin_reset_password(self, email: str, new_password: str) -> Dict:
        """Admin function to directly reset user password"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Update user password directly
            result = await db.users.update_one(
                {"email": email},
                {"$set": {
                    "password_hash": self._hash_password(new_password),
                    "updated_at": datetime.now()
                }}
            )

            if result.modified_count > 0:
                return {"status": True, "message": f"Password reset successfully for {email}"}
            else:
                return {"status": False, "message": "User not found"}

        except Exception as e:
            return {"status": False, "message": f"Error resetting password: {str(e)}"}

    async def update_user_role_by_email(self, email: str, new_role: str) -> Dict:
        """Update user role by email"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            result = await db.users.update_one(
                {"email": email},
                {"$set": {"role": new_role, "updated_at": datetime.now()}}
            )

            if result.modified_count > 0:
                return {"status": True, "message": f"User role updated to {new_role}"}
            else:
                return {"status": False, "message": "User not found"}

        except Exception as e:
            return {"status": False, "message": f"Error updating user role: {str(e)}"}

    async def update_user_ib_proof(self, user_id: str, update_data: Dict) -> Dict:
        """Update user with IB proof and broker details"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Hash trading password if provided
            if "trading_password_hash" in update_data and update_data["trading_password_hash"]:
                update_data["trading_password_hash"] = self._hash_password(update_data["trading_password_hash"])

            # Add updated_at timestamp
            update_data["updated_at"] = datetime.now()

            result = await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )

            if result.modified_count > 0:
                return {"status": True, "message": "User IB proof updated successfully"}
            else:
                return {"status": False, "message": "User not found or no changes made"}

        except Exception as e:
            return {"status": False, "message": f"Error updating user IB proof: {str(e)}"}

    async def approve_user_ib(self, user_id: str, approver_id: Optional[str] = None) -> Dict:
        """Approve a user's IB proof and mark account active"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            result = await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"ib_status": "approved", "ib_approval_date": datetime.now(), "ib_approved_by": approver_id, "status": "active", "updated_at": datetime.now()}}
            )

            if result.modified_count > 0:
                return {"status": True, "message": "User IB approved and account activated"}
            else:
                return {"status": False, "message": "User not found or no changes made"}

        except Exception as e:
            return {"status": False, "message": f"Error approving user IB: {str(e)}"}

    # ===================================
    # COPY TRADING PLATFORM FUNCTIONS
    # ===================================

    # TRADING ACCOUNTS
    async def create_trading_account(self, account_data: Dict) -> Dict:
        """Create a new trading account"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Check if account already exists
            existing = await db.trading_accounts.find_one({
                "account_number": account_data["account_number"],
                "broker": account_data["broker"]
            })
            if existing:
                return {"status": False, "message": "Account already exists"}

            # Encrypt trading password
            if "trading_password" in account_data:
                account_data["trading_password_hash"] = self._hash_password(account_data["trading_password"])
                del account_data["trading_password"]

            account_data["created_at"] = datetime.now()
            account_data["updated_at"] = datetime.now()

            result = await db.trading_accounts.insert_one(account_data)
            return {
                "status": True,
                "message": "Trading account created successfully",
                "data": {"account_id": str(result.inserted_id)}
            }

        except Exception as e:
            return {"status": False, "message": f"Error creating trading account: {str(e)}"}

    async def get_user_accounts(self, user_id: str) -> Dict:
        """Get all trading accounts for a user"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            cursor = db.trading_accounts.find({"user_id": user_id})
            accounts = await cursor.to_list(length=None)

            # Mask account numbers for security
            for account in accounts:
                account["id"] = str(account["_id"])
                account["account_number_masked"] = "*" * (len(account["account_number"]) - 4) + account["account_number"][-4:]
                del account["_id"]
                if "trading_password_hash" in account:
                    del account["trading_password_hash"]

            return {"status": True, "data": {"accounts": accounts}}

        except Exception as e:
            return {"status": False, "message": f"Error fetching accounts: {str(e)}"}

    async def update_account_status(self, account_id: str, status: str, group_id: str = None) -> Dict:
        """Update trading account status and group assignment"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            update_data = {"status": status, "updated_at": datetime.now()}
            if group_id:
                update_data["group_id"] = group_id
                if status == "approved":
                    update_data["copy_start_date"] = datetime.now()
                    update_data["copy_status"] = "active"

            result = await db.trading_accounts.update_one(
                {"_id": ObjectId(account_id)},
                {"$set": update_data}
            )

            if result.modified_count > 0:
                # Also update user's group assignment
                if group_id and status == "approved":
                    account = await db.trading_accounts.find_one({"_id": ObjectId(account_id)})
                    if account:
                        await db.users.update_one(
                            {"_id": ObjectId(account["user_id"])},
                            {"$set": {
                                "group_id": group_id,
                                "group_join_date": datetime.now(),
                                "updated_at": datetime.now()
                            }}
                        )

                return {"status": True, "message": f"Account status updated to {status}"}
            else:
                return {"status": False, "message": "Account not found"}

        except Exception as e:
            return {"status": False, "message": f"Error updating account status: {str(e)}"}

    # TRADING GROUPS
    async def create_trading_group(self, group_data: Dict) -> Dict:
        """Create a new trading group"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Check if group name exists
            existing = await db.trading_groups.find_one({"group_name": group_data["group_name"]})
            if existing:
                return {"status": False, "message": "Group name already exists"}

            group_data["created_at"] = datetime.now()
            group_data["updated_at"] = datetime.now()
            group_data["api_key"] = secrets.token_urlsafe(32)

            result = await db.trading_groups.insert_one(group_data)
            return {
                "status": True,
                "message": "Trading group created successfully",
                "data": {"group_id": str(result.inserted_id), "api_key": group_data["api_key"]}
            }

        except Exception as e:
            return {"status": False, "message": f"Error creating trading group: {str(e)}"}

    async def get_trading_groups(self, group_leader_id: str = None) -> Dict:
        """Get all trading groups or groups for specific leader"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            query = {}
            if group_leader_id:
                query["group_leader_id"] = group_leader_id

            cursor = db.trading_groups.find(query).sort("created_at", -1)
            groups = await cursor.to_list(length=None)

            for group in groups:
                group["id"] = str(group["_id"])
                del group["_id"]

            return {"status": True, "data": {"groups": groups}}

        except Exception as e:
            return {"status": False, "message": f"Error fetching trading groups: {str(e)}"}

    async def update_group_trading_status(self, group_id: str, status: str, updated_by: str) -> Dict:
        """Update group trading status"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            result = await db.trading_groups.update_one(
                {"_id": ObjectId(group_id)},
                {"$set": {
                    "trading_status": status,
                    "updated_at": datetime.now(),
                    "last_updated_by": updated_by
                }}
            )

            if result.modified_count > 0:
                # Update all accounts in this group
                await db.trading_accounts.update_many(
                    {"group_id": group_id},
                    {"$set": {"copy_status": status, "updated_at": datetime.now()}}
                )
                return {"status": True, "message": f"Group trading status updated to {status}"}
            else:
                return {"status": False, "message": "Group not found"}

        except Exception as e:
            return {"status": False, "message": f"Error updating group status: {str(e)}"}

    # DASHBOARD DATA
    async def get_user_dashboard_data(self, user_id: str) -> Dict:
        """Get dashboard data for user panel"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Get user's accounts
            accounts_cursor = db.trading_accounts.find({"user_id": user_id})
            accounts = await accounts_cursor.to_list(length=None)

            total_equity = sum(acc.get("equity", 0) for acc in accounts)
            total_profit = sum(acc.get("profit_since_copy_start", 0) for acc in accounts)
            total_withdrawal = sum(acc.get("total_withdrawal", 0) for acc in accounts)
            running_trades = sum(acc.get("running_trades_count", 0) for acc in accounts)

            # Calculate today's profit (mock for now)
            today_profit = total_profit * 0.1  # Example calculation

            # Get copy status
            copy_status = "Active" if any(acc.get("copy_status") == "active" for acc in accounts) else "Inactive"

            dashboard_data = {
                "total_equity": total_equity,
                "total_profit": total_profit,
                "profit_percentage": (total_profit / total_equity * 100) if total_equity > 0 else 0,
                "today_profit": today_profit,
                "total_withdrawal": total_withdrawal,
                "running_trades": running_trades,
                "copy_status": copy_status,
                "accounts_count": len(accounts)
            }

            return {"status": True, "data": dashboard_data}

        except Exception as e:
            return {"status": False, "message": f"Error fetching dashboard data: {str(e)}"}

    async def get_admin_dashboard_data(self) -> Dict:
        """Get dashboard data for admin panel"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Count active users
            active_users = await db.users.count_documents({"status": "active"})

            # Count groups
            total_groups = await db.trading_groups.count_documents({})

            # Sum total equity and profit from all accounts
            accounts_cursor = db.trading_accounts.find({"status": "approved"})
            accounts = await accounts_cursor.to_list(length=None)

            total_equity = sum(acc.get("equity", 0) for acc in accounts)
            total_profit = sum(acc.get("profit_since_copy_start", 0) for acc in accounts)
            today_profit = total_profit * 0.05  # Mock calculation
            running_trades = sum(acc.get("running_trades_count", 0) for acc in accounts)

            # Get pending settlements
            pending_settlements = await db.settlements.find({"status": "pending"}).to_list(length=None)
            pending_settlement_amount = sum(s.get("amount_due", 0) for s in pending_settlements)

            # Count errors
            error_count = await db.error_logs.count_documents({"resolved": False})

            dashboard_data = {
                "active_users": active_users,
                "total_groups": total_groups,
                "total_equity": total_equity,
                "total_profit": total_profit,
                "today_profit": today_profit,
                "running_trades": running_trades,
                "pending_settlement_amount": pending_settlement_amount,
                "error_count": error_count
            }

            return {"status": True, "data": dashboard_data}

        except Exception as e:
            return {"status": False, "message": f"Error fetching admin dashboard data: {str(e)}"}

    async def get_group_dashboard_data(self, group_id: str) -> Dict:
        """Get dashboard data for group panel"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            # Get group info
            group = await db.trading_groups.find_one({"_id": ObjectId(group_id)})
            if not group:
                return {"status": False, "message": "Group not found"}

            # Get accounts in this group
            accounts_cursor = db.trading_accounts.find({"group_id": group_id, "status": "approved"})
            accounts = await accounts_cursor.to_list(length=None)

            active_users = len([acc for acc in accounts if acc.get("copy_status") == "active"])
            total_equity = sum(acc.get("equity", 0) for acc in accounts)
            total_profit = sum(acc.get("profit_since_copy_start", 0) for acc in accounts)
            today_profit = total_profit * 0.03  # Mock calculation
            running_trades = sum(acc.get("running_trades_count", 0) for acc in accounts)

            # Get pending settlements for this group
            pending_settlements = await db.settlements.find({
                "group_id": group_id,
                "status": "pending"
            }).to_list(length=None)
            pending_settlement_amount = sum(s.get("amount_due", 0) for s in pending_settlements)

            # Count errors for this group
            error_count = await db.error_logs.count_documents({
                "group_id": group_id,
                "resolved": False
            })

            dashboard_data = {
                "group_name": group["group_name"],
                "active_users": active_users,
                "total_users": len(accounts),
                "total_equity": total_equity,
                "total_profit": total_profit,
                "today_profit": today_profit,
                "running_trades": running_trades,
                "pending_settlement_amount": pending_settlement_amount,
                "error_count": error_count
            }

            return {"status": True, "data": dashboard_data}

        except Exception as e:
            return {"status": False, "message": f"Error fetching group dashboard data: {str(e)}"}

    # SETTLEMENTS
    async def create_settlement(self, settlement_data: Dict) -> Dict:
        """Create a new settlement record"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            settlement_data["created_at"] = datetime.now()
            settlement_data["updated_at"] = datetime.now()

            result = await db.settlements.insert_one(settlement_data)
            return {
                "status": True,
                "message": "Settlement created successfully",
                "data": {"settlement_id": str(result.inserted_id)}
            }

        except Exception as e:
            return {"status": False, "message": f"Error creating settlement: {str(e)}"}

    async def get_settlements(self, group_id: str = None) -> Dict:
        """Get settlements for a group or all settlements"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            query = {}
            if group_id:
                query["group_id"] = group_id

            cursor = db.settlements.find(query).sort("created_at", -1)
            settlements = await cursor.to_list(length=None)

            for settlement in settlements:
                settlement["id"] = str(settlement["_id"])
                del settlement["_id"]

            return {"status": True, "data": {"settlements": settlements}}

        except Exception as e:
            return {"status": False, "message": f"Error fetching settlements: {str(e)}"}

    # ERROR LOGGING
    async def log_error(self, error_data: Dict) -> Dict:
        """Log an error"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            error_data["created_at"] = datetime.now()
            result = await db.error_logs.insert_one(error_data)

            return {
                "status": True,
                "message": "Error logged successfully",
                "data": {"error_id": str(result.inserted_id)}
            }

        except Exception as e:
            return {"status": False, "message": f"Error logging error: {str(e)}"}

    async def get_error_logs(self, group_id: str = None, resolved: bool = None) -> Dict:
        """Get error logs"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            query = {}
            if group_id:
                query["group_id"] = group_id
            if resolved is not None:
                query["resolved"] = resolved

            cursor = db.error_logs.find(query).sort("created_at", -1).limit(100)
            errors = await cursor.to_list(length=None)

            for error in errors:
                error["id"] = str(error["_id"])
                del error["_id"]

            return {"status": True, "data": {"errors": errors}}

        except Exception as e:
            return {"status": False, "message": f"Error fetching error logs: {str(e)}"}

    # SUPPORT TICKETS
    async def create_support_ticket(self, ticket_data: Dict) -> Dict:
        """Create a support ticket"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            ticket_data["created_at"] = datetime.now()
            ticket_data["updated_at"] = datetime.now()
            ticket_data["messages"] = []

            result = await db.support_tickets.insert_one(ticket_data)
            return {
                "status": True,
                "message": "Support ticket created successfully",
                "data": {"ticket_id": str(result.inserted_id)}
            }

        except Exception as e:
            return {"status": False, "message": f"Error creating support ticket: {str(e)}"}

    async def get_user_support_tickets(self, user_id: str) -> Dict:
        """Get support tickets for a user"""
        try:
            db = self.get_db()
            if db is None:
                return {"status": False, "message": "Database connection not available"}

            cursor = db.support_tickets.find({"user_id": user_id}).sort("created_at", -1)
            tickets = await cursor.to_list(length=None)

            for ticket in tickets:
                ticket["id"] = str(ticket["_id"])
                del ticket["_id"]

            return {"status": True, "data": {"tickets": tickets}}

        except Exception as e:
            return {"status": False, "message": f"Error fetching support tickets: {str(e)}"}


# Create singleton instance
mongodb_service = MongoDBService()

# Standalone functions for compatibility
async def get_user_by_id(user_id: str) -> Dict:
    """Get user by ID - standalone function"""
    return await mongodb_service.get_user_by_id(user_id)

async def get_user_by_email(email: str) -> Dict:
    """Get user by email - standalone function"""
    return await mongodb_service.get_user_by_email(email)