from fastapi import APIRouter, HTTPException, status, Depends
from backend.core.config import settings
from backend.utils.mongo import fetch_documents
from backend.models.common import APIResponse

# Import admin verify dependency
from backend.api.admin import verify_admin

router = APIRouter()


@router.get("/api/all-masters", response_model=APIResponse)
async def get_all_masters(admin_user = Depends(verify_admin)):
    """Return all master traders (admin only). Tries `master_traders` then `master_accounts`."""
    try:
        # Try master_traders collection first
        res = fetch_documents(settings.DATABASE_NAME, "master_traders", {}, sort=[("created_at", -1)])
        masters = []
        if res.get("status") and res.get("data"):
            masters = res.get("data")
        else:
            # Fallback to master_accounts collection
            res2 = fetch_documents(settings.DATABASE_NAME, "master_accounts", {}, sort=[("created_at", -1)])
            if res2.get("status"):
                masters = res2.get("data")

        # Strip sensitive fields before returning
        safe_masters = []
        for m in masters:
            safe = m.copy()
            for sensitive in ("password", "trading_password_hash", "api_key", "secret"):
                if sensitive in safe:
                    safe.pop(sensitive, None)
            safe_masters.append(safe)

        return APIResponse(success=True, message="Master traders retrieved", data={"masters": safe_masters})

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
