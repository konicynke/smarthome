import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.concurrency import run_in_threadpool

from app import repository
from app.config import ONLINE_TIMEOUT_SECONDS
from app.db import get_conn
from app.live import hub
from app.schemas import DeviceOut, ReadingOut, ReadingPayload

router = APIRouter(prefix="/api/readings", tags=["readings"])
logger = logging.getLogger(__name__)


def store_reading(conn, payload):
    try:
        with conn.cursor() as cur:
            repository.upsert_device(
                cur, payload.device_id, payload.room, payload.type, payload.source
            )
            repository.insert_reading(cur, payload.device_id, payload.values)
            device = repository.get_device(cur, payload.device_id, ONLINE_TIMEOUT_SECONDS)
        conn.commit()
        return device
    except Exception:
        conn.rollback()
        raise


@router.post("")
async def add_reading(payload: ReadingPayload, conn=Depends(get_conn)):
    try:
        device = await run_in_threadpool(store_reading, conn, payload)
    except Exception:
        logger.exception("reading write unsuccessful: %s", payload.device_id)
        raise HTTPException(status_code=500, detail="Internal server error")
    await hub.broadcast(
        {"type": "reading", "device": DeviceOut.model_validate(device).model_dump(mode="json")}
    )
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
