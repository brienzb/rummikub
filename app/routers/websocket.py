from fastapi import APIRouter
from fastapi import WebSocket, WebSocketDisconnect

from app.internal.client import user_manager, room_manager

websocket = APIRouter(
    prefix="/websocket",
    tags=["websocket"],
)


@websocket.websocket("/{room_id}/{user_id}")
async def websocket_endpoint(ws: WebSocket, room_id: str, user_id: str):
    # TODO: user 및 room 존재 하는지 확인 필요?!
    this_user = user_manager.get_user(user_id)

    await room_manager.connect_room(room_id=room_id, websocket=ws)
    await room_manager.broadcast_room(
        room_id=room_id,
        message=f"{this_user.nickname} ({this_user.user_id}) 님이 방에 들어왔습니다.",
    )

    try:
        while True:
            data = await ws.receive_text()
            await room_manager.broadcast_room(
                room_id=room_id,
                message=f"{this_user.nickname} ({this_user.user_id}) : {data}",
            )
    except WebSocketDisconnect:
        room_manager.disconnect_room(room_id=room_id, websocket=ws)
        room_manager.leave_room(room_id=room_id, user=this_user)
        await room_manager.broadcast_room(
            room_id=room_id,
            message=f"{this_user.nickname} ({this_user.user_id}) 님이 방을 나갔습니다.",
        )
