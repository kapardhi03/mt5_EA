from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, date
import uuid
from backend.core.config import settings
from backend.utils.mongo import insert_document, fetch_documents, count_documents
from backend.utils.encryption import encrypt_string

router = APIRouter()

class MasterTraderCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=6)
    mobile_number: str = Field(..., min_length=6)
    no_of_slave: int = Field(..., ge=0)
    status: bool = True
    start_date: date
    end_date: date

@router.post("/api/master-add")
async def master_add(request: Request, payload: MasterTraderCreate):
    """Create a new master trader. Validates client IP, master limits, duplicates, dates and assigns MT5 path."""
    try:
        # Get client IP
        client_host = request.client.host if request.client else None
        client_ip = client_host or request.headers.get('x-forwarded-for', '')

        # IP validation
        restricted = settings.RESTRICTED_IPS or ["0"]
        if not (len(restricted) == 0 or "0" in restricted):
            # restricted list exists and wildcard not present
            if client_ip not in restricted:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This IP is not allowed to access this API")

        # Date validation
        start_dt = datetime.combine(payload.start_date, datetime.min.time())
        end_dt = datetime.combine(payload.end_date, datetime.min.time())
        if end_dt < start_dt:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="End date cannot be before start date")

        # Master account limit
        count_res = count_documents(settings.DATABASE_NAME, "master_accounts", {})
        if not count_res.get("status"):
            # DB error - but proceed cautiously
            raise HTTPException(status_code=500, detail=f"Internal server error: {count_res.get('error')}")
        total_masters = count_res.get("data", 0)
        if total_masters >= settings.MAX_MASTER_FOLDER:
            raise HTTPException(status_code=400, detail="Maximum master account limit reached")

        # Duplicate email check (users and master_traders collections)
        users_res = fetch_documents(settings.DATABASE_NAME, "users", {"email": payload.email})
        if users_res.get("status") and users_res.get("data"):
            raise HTTPException(status_code=400, detail="Email already exists or failed to insert")

        masters_res = fetch_documents(settings.DATABASE_NAME, "master_traders", {"email": payload.email})
        if masters_res.get("status") and masters_res.get("data"):
            raise HTTPException(status_code=400, detail="Email already exists or failed to insert")

        # Determine MT5 path (next available)
        existing = fetch_documents(settings.DATABASE_NAME, "master_traders", {}, sort=[("created_at", -1)])
        next_path_index = 1
        if existing.get("status") and existing.get("data"):
            paths = []
            for doc in existing.get("data"):
                p = doc.get("mt5_path")
                if p and isinstance(p, str) and p.startswith("mt5_path_"):
                    try:
                        idx = int(p.split("mt5_path_")[-1])
                        paths.append(idx)
                    except Exception:
                        continue
            if paths:
                next_path_index = max(paths) + 1

        mt5_path = f"mt5_path_{next_path_index}"

        # Prepare master trader record
        master_record = {
            "master_id": str(uuid.uuid4()),
            "name": payload.name,
            "email": payload.email,
            "password": encrypt_string(payload.password),
            "mobile_number": payload.mobile_number,
            "no_of_slave": payload.no_of_slave,
            "status": "active" if payload.status else "inactive",
            "start_date": start_dt,
            "end_date": end_dt,
            "mt5_path": mt5_path,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        ins = insert_document(settings.DATABASE_NAME, "master_traders", master_record)
        if not ins.get("status"):
            raise HTTPException(status_code=400, detail="Email already exists or failed to insert")

        # Log admin activity
        try:
            log = {
                "action": "master_add",
                "details": f"Master trader {payload.email} added",
                "client_ip": client_ip,
                "created_at": datetime.utcnow()
            }
            insert_document(settings.DATABASE_NAME, "admin_logs", log)
        except Exception:
            # Logging failure should not block API
            pass

        return {"status": "success", "message": f"Master trader '{payload.name}' added successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
