from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from app.live import hub
from app.security import decode_token

router = APIRouter()


@router.websocket("/ws")
async def live(websocket: WebSocket, token: str = Query(default="")):
    if decode_token(token) is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await hub.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        hub.disconnect(websocket)
