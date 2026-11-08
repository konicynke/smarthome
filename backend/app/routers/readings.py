import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app import repository
from app.db import get_conn
from app.schemas import ReadingOut, ReadingPayload

router = APIRouter(prefix="/api/readings", tags=["readings"])
logger = logging.getLogger(__name__)


@router.post("")
def add_reading(payload: ReadingPayload, conn=Depends(get_conn)):
    try:
        with conn.cursor() as cur:
            repository.upsert_device(
                cur, payload.device_id, payload.room, payload.type, payload.source
            )
            repository.insert_reading(cur, payload.device_id, payload.values)
        conn.commit()
    except Exception:
        conn.rollback()
        logger.exception("reading write unsuccessful: %s", payload.device_id)
        raise HTTPException(status_code=500, detail="Internal server error")
    return {"status": "ok"}


@router.get("", response_model=List[ReadingOut])
def get_readings(
    device_id: str,
    ts_from: Optional[datetime] = Query(None, alias="from"),
    ts_to: Optional[datetime] = Query(None, alias="to"),
    limit: int = Query(500, ge=1, le=5000),
    conn=Depends(get_conn),
):
    with conn.cursor() as cur:
        return repository.get_readings(cur, device_id, ts_from, ts_to, limit)