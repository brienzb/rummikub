from fastapi import APIRouter
from fastapi import WebSocket, WebSocketDisconnect

from app.internal.client import client_manager as manager

websocket = APIRouter(
    prefix="/websocket",
    tags=["websocket"],
)


@websocket.websocket("/{client_id}")
async def websocket_endpoint(ws: WebSocket, client_id: str):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", ws)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(ws)
        await manager.broadcast(f"Client #{client_id} left the chat")
