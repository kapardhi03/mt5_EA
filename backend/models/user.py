"""
Clean User Models for MT5 Copy Trading Platform
Organized and optimized user-related models
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Literal
from datetime import datetime

# ===================================
# Request Models (Input)
# ===================================

class UserRegistration(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    mobile: str = Field(..., min_length=10, max_length=15, description="Mobile number with country code")
    email: EmailStr = Field(..., description="Email address")
    country: str = Field(..., min_length=2, max_length=50, description="Country")
    state: str = Field(..., min_length=2, max_length=50, description="State")
    city: str = Field(..., min_length=2, max_length=50, description="City")
    pin_code: str = Field(..., min_length=4, max_length=10, description="PIN/ZIP code")
    password: str = Field(..., min_length=8, max_length=100, description="Password (min 8 characters)")
    broker: str = Field(..., min_length=2, max_length=50, description="Selected broker")
    account_no: str = Field(..., min_length=4, max_length=20, description="Trading account number")
    trading_password: str = Field(..., min_length=4, max_length=100, description="Trading account password")
    referral_code: Optional[str] = Field(None, description="Group referral code or API key")

    @validator('mobile')
    def validate_mobile(cls, v):
        # Remove spaces and hyphens
        cleaned = v.replace(' ', '').replace('-', '')

        # Ensure it starts with + for international format
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

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserLogin(BaseModel):
    mobile_or_email: str = Field(..., description="Email or mobile number")
    password: str = Field(..., description="Password")

class OTPRequest(BaseModel):
    mobile_or_email: str = Field(..., description="Email or mobile number")
    otp_type: Literal["mobile", "email"] = Field(..., description="Type of OTP")

class OTPVerification(BaseModel):
    mobile_or_email: str = Field(..., description="Email or mobile number")
    otp: str = Field(..., min_length=4, max_length=8, description="OTP code")
    otp_type: Literal["mobile", "email"] = Field(..., description="Type of OTP")

class PasswordReset(BaseModel):
    mobile_or_email: str = Field(..., description="Email or mobile number")
    otp: str = Field(..., min_length=4, max_length=8, description="OTP code")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")

class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    country: Optional[str] = Field(None, min_length=2, max_length=50)
    state: Optional[str] = Field(None, min_length=2, max_length=50)
    city: Optional[str] = Field(None, min_length=2, max_length=50)
    pin_code: Optional[str] = Field(None, min_length=4, max_length=10)

class IBProofUpload(BaseModel):
    proof_image: str = Field(..., description="Base64 encoded image data")
    broker: str = Field(..., description="Selected broker name")
    account_number: str = Field(..., description="Trading account number")
    trading_password: str = Field(..., description="Trading account password")
    proof_filename: Optional[str] = Field(None, description="Original filename of the uploaded proof image")

class IBProofAction(BaseModel):
    user_id: str = Field(..., description="User ID for IB proof action")
    action: Literal["approve", "reject"] = Field(..., description="Action to take")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection (required if action is reject)")

class GroupJoinRequest(BaseModel):
    referral_code: str = Field(..., min_length=8, max_length=50, description="Group referral code or API key")

# ===================================
# Response Models (Output)
# ===================================

class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    mobile: str
    country: str
    state: str
    city: str
    pin_code: str
    role: str
    status: str
    mobile_verified: bool
    email_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user: UserProfile

class LoginResponse(BaseModel):
    success: bool
    message: str
    data: Optional[TokenResponse] = None

class RegistrationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class OTPResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None  # Contains OTP in demo mode

# ===================================
# Database Models (Internal)
# ===================================

class UserRole:
    USER = "user"
    ADMIN = "admin"
    MASTER = "master"
    GROUP_MANAGER = "group_manager"
    ACCOUNTANT = "accountant"
    SUPPORT = "support"

class UserStatus:
    PENDING = "pending"
    PENDING_IB_CHANGE = "pending_ib_change"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REJECTED = "rejected"

class IBStatus:
    NOT_CHANGED = "not_changed"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class UserDocument(BaseModel):
    """Database document model for users"""
    id: Optional[str] = Field(None, alias="_id")
    name: str
    mobile: str
    email: str
    country: str
    state: str
    city: str
    pin_code: str
    password_hash: str
    role: str = UserRole.USER
    status: str = UserStatus.PENDING
    mobile_verified: bool = False
    email_verified: bool = False

    # Broker and account details
    broker: Optional[str] = None
    account_no: Optional[str] = None
    trading_password_hash: Optional[str] = None

    # IB change workflow
    ib_status: str = IBStatus.NOT_CHANGED
    ib_proof_filename: Optional[str] = None
    ib_proof_upload_date: Optional[datetime] = None
    ib_approval_date: Optional[datetime] = None
    ib_approved_by: Optional[str] = None
    ib_rejection_reason: Optional[str] = None
    ib_proof_image_data: Optional[str] = None  # Base64 encoded image data
    ib_proof_image_url: Optional[str] = None  # URL to stored image

    # Group membership
    group_id: Optional[str] = None
    group_join_date: Optional[datetime] = None
    referral_code_used: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    login_attempts: int = 0
    locked_until: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }