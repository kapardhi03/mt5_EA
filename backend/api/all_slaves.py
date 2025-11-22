from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional

from backend.core.config import settings
from backend.utils.mongo import fetch_documents
from backend.services.user_service import user_service
from backend.api.admin import verify_admin
from backend.models.common import APIResponse

router = APIRouter()


@router.get("/api/all-slaves", response_model=APIResponse)
async def get_all_slaves(
    role: Optional[str] = Query(None, description="Filter by role (e.g., member)"),
    status: Optional[str] = Query(None, description="Filter by user status"),
    admin_user = Depends(verify_admin)
):
    """Return list of users (slave traders). Admin only."""

    try:
        # Default to listing regular members unless a role is provided
        query = {}
        if role:
            query["role"] = role
        else:
            query["role"] = "member"

        # Exclude deleted users
        query["status"] = {"$ne": "deleted"} if not status else status

        result = fetch_documents(
            settings.DATABASE_NAME,
            "users",
            query,
            sort=[("created_at", -1)]
        )

        if not result["status"]:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result.get("error", "DB error"))

        users = result.get("data", [])

        # Clean sensitive fields
        cleaned = [user_service.clean_user_data(u) for u in users]

        return APIResponse(success=True, message="Slave users retrieved", data=cleaned)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
