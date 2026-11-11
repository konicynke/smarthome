from typing import List

from fastapi import APIRouter, Depends

from app import repository
from app.config import ONLINE_TIMEOUT_SECONDS
from app.db import get_conn
from app.schemas import DeviceOut
from app.security import require_user

router = APIRouter(
    prefix="/api/devices", tags=["devices"], dependencies=[Depends(require_user)]
)


@router.get("", response_model=List[DeviceOut])
def get_devices(conn=Depends(get_conn)):
    with conn.cursor() as cur:
        return repository.list_devices(cur, ONLINE_TIMEOUT_SECONDS)