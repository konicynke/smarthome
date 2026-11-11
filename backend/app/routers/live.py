from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.live import hub

router = APIRouter()


@router.websocket("/ws")
async def live(websocket: WebSocket):
    await hub.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        hub.disconnect(websocket)
