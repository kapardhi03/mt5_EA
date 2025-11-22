from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel, Field
from backend.core.config import settings
from backend.utils.mongo import update_document, insert_document, fetch_documents
from datetime import datetime
from zoneinfo import ZoneInfo

router = APIRouter()


class LogInMasterRequest(BaseModel):
    trade_id: int = Field(...)
    mt_account_no: int = Field(...)
    mt_password: str = Field(..., min_length=1)
    mt_server: str = Field(..., min_length=1)


@router.post("/api/master-login")
async def master_login(request: Request, payload: LogInMasterRequest):
    """Update a master trader's MT5 login credentials (IP-restricted).

    Stores MT5 login JSON and account number, resets stale fields, and logs action.
    """
    try:
        # Resolve client IP
        client_host = request.client.host if request.client else None
        client_ip = client_host or request.headers.get('x-forwarded-for', '')

        # IP validation against settings.RESTRICTED_IPS
        restricted = settings.RESTRICTED_IPS or ["0"]
        if not (len(restricted) == 0 or "0" in restricted):
            if client_ip not in restricted:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This IP is not allowed to access this API")

        # Prepare MT5 login JSON
        mt5_login = {
            "server": payload.mt_server,
            "account": str(payload.mt_account_no),
            "password": payload.mt_password
        }

        # Reset irrelevant fields to prevent stale data
        clear_marker = "__CLEAR__"
        update_data = {
            "mt5_login": mt5_login,
            "mt5_account_no": payload.mt_account_no,
            "account_name": clear_marker,
            "balance": clear_marker,
            "equity": clear_marker,
            "free_margin": clear_marker,
            "profit_till_date": clear_marker,
            "last_trade_sync": clear_marker,
            "open_positions": clear_marker,
            "connection_status": clear_marker,
            "updated_at": datetime.utcnow()
        }

        # Attempt to update document by trade_id
        res = update_document(settings.DATABASE_NAME, "master_traders", "trade_id", payload.trade_id, update_data)
        if not res.get("status"):
            # If update failed or no document modified, return 400
            raise HTTPException(status_code=400, detail="Failed to update MT5 login data")

        # Log admin activity (admin_id=0 per spec)
        try:
            tz = ZoneInfo("Asia/Kolkata")
            log = {
                "admin_id": 0,
                "action": "master_login_update",
                "entity": "master_traders",
                "entity_id": payload.trade_id,
                "client_ip": client_ip,
                "details": {
                    "mt5_account_no": payload.mt_account_no,
                    "server": payload.mt_server
                },
                "update_time": datetime.now(tz).isoformat()
            }
            insert_document(settings.DATABASE_NAME, "admin_logs", log)
        except Exception:
            pass

        return {
            "status": "success",
            "message": f"MT5 login updated for trade_id={payload.trade_id}",
            "data": {
                "trade_id": payload.trade_id,
                "account_no": payload.mt_account_no,
                "server": payload.mt_server
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
