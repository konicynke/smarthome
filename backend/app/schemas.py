from datetime import datetime
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel

DeviceType = Literal["temp_humidity", "illuminance", "motion", "gas"]
Source = Literal["real", "sim"]


class ReadingPayload(BaseModel):
    device_id: str
    room: str
    type: DeviceType
    source: Source
    values: Dict[str, Any]


class ReadingOut(BaseModel):
    ts: datetime
    data: Dict[str, Any]


class DeviceOut(BaseModel):
    device_id: str
    room: str
    type: str
    source: str
    last_seen: datetime
    online: bool
    last_reading: Optional[ReadingOut]