from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel, Field
from backend.core.config import settings
from backend.utils.mongo import fetch_documents, delete_document, insert_document
from datetime import datetime
from zoneinfo import ZoneInfo

router = APIRouter()


class DeleteMasterRequest(BaseModel):
    trade_id: int = Field(..., gt=0, description="Unique identifier of the master trader to delete")


@router.delete("/api/master-delete")
async def master_delete(request: Request, payload: DeleteMasterRequest):
    """Delete a master trader by trade_id (IP-restricted). Logs the deletion action."""
    try:
        # Resolve client IP
        client_host = request.client.host if request.client else None
        client_ip = client_host or request.headers.get('x-forwarded-for', '')

        # IP validation
        restricted = settings.RESTRICTED_IPS or ["0"]
        if not (len(restricted) == 0 or "0" in restricted):
            if client_ip not in restricted:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This IP is not allowed to access this API")

        trade_id = payload.trade_id

        # Verify master trader exists
        found = fetch_documents(settings.DATABASE_NAME, "master_traders", {"trade_id": trade_id})
        if not found.get("status"):
            raise HTTPException(status_code=500, detail="Internal server error: failed to query database")

        if not found.get("data"):
            raise HTTPException(status_code=404, detail=f"No master trader found with trade_id {trade_id}")

        # Perform deletion
        del_res = delete_document(settings.DATABASE_NAME, "master_traders", {"trade_id": trade_id})
        if not del_res.get("status"):
            raise HTTPException(status_code=500, detail=f"Internal server error: {del_res.get('error')}")

        # Check deletion count from del_res.data (string like 'Deleted X document(s)')
        deleted_info = del_res.get("data", "")
        if "Deleted 0" in deleted_info:
            # Nothing deleted
            raise HTTPException(status_code=404, detail=f"No master trader found with trade_id {trade_id}")

        # Log deletion (admin_id=0)
        try:
            tz = ZoneInfo("Asia/Kolkata")
            log = {
                "admin_id": 0,
                "action": "master_delete",
                "entity": "master_traders",
                "entity_id": trade_id,
                "client_ip": client_ip,
                "details": {"deleted_info": deleted_info},
                "update_time": datetime.now(tz).isoformat()
            }
            insert_document(settings.DATABASE_NAME, "admin_logs", log)
        except Exception:
            pass

        return {
            "status": "success",
            "message": f"Master trader with trade_id {trade_id} deleted successfully",
            "requested_by_ip": client_ip
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
