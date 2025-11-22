from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """Generic API response model"""
    success: bool
    message: str
    data: Optional[T] = None
    error: Optional[str] = None

    @classmethod
    def success_response(cls, data: T = None, message: str = "Success"):
        return cls(success=True, message=message, data=data)

    @classmethod
    def error_response(cls, message: str, error: str = None):
        return cls(success=False, message=message, error=error)

class BasicResponse(BaseModel):
    """Basic response without data"""
    success: bool
    message: str
    error: Optional[str] = None

class LoginResponse(BaseModel):
    """Login response with token"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    expires_in: int = 3600

class RegistrationStepResponse(BaseModel):
    """Registration step response"""
    step_completed: int
    next_step: Optional[int] = None
    temp_user_id: str
    message: str

class DashboardResponse(BaseModel):
    """Dashboard data response"""
    user_info: dict
    statistics: dict
    recent_activities: list