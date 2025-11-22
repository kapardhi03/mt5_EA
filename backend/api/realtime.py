"""
Real-time API endpoints using Server-Sent Events (SSE)
"""

from fastapi import APIRouter, Depends, Request
from backend.core.security import get_current_user
from backend.services.realtime_service import sse_endpoint
from backend.services.mongodb_service import mongodb_service
from bson import ObjectId

router = APIRouter()

@router.get("/events")
async def get_realtime_events(
    request: Request,
    current_user_id: str = Depends(get_current_user)
):
    """SSE endpoint for real-time updates"""
    # Get user role from database
    db = mongodb_service.get_db()
    if db:
        user = await db.users.find_one({"_id": ObjectId(current_user_id)})
        user_role = user.get("role", "user") if user else "user"
    else:
        user_role = "user"

    return await sse_endpoint(request, current_user_id, user_role)