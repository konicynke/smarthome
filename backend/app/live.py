import asyncio
import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class LiveHub:
    def __init__(self):
        self._clients = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self._clients.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self._clients.discard(websocket)

    async def broadcast(self, message):
        clients = list(self._clients)
        if not clients:
            return
        results = await asyncio.gather(
            *(client.send_json(message) for client in clients),
            return_exceptions=True,
        )
        for client, result in zip(clients, results):
            if isinstance(result, Exception):
                logger.info("dropping live client: %s", result)
                self.disconnect(client)


hub = LiveHub()
