# ===================================
# models/common.py
# ===================================
from pydantic import BaseModel, Field
from typing import Optional, Any

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[dict] = None

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    
class PaginatedResponse(BaseModel):
    success: bool
    message: str
    data: list
    pagination: dict