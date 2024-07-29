import random

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from app.internal.templates import get_template_response

room = APIRouter(
    prefix="/room",
    tags=["room"],
)


# [TODO] room_pool 싱글톤 객체로 구현 (혹은 다른 무언가..)
room_pool = []


@room.post("/create")
async def create_room(request: Request) -> int:
    # [TODO] room_id 생성 로직 구현
    room_id = random.randint(10000, 99999)

    room_pool.append(room_id)
    print("current room pool status:", room_pool)

    return room_id


@room.get("/{room_id}")
async def get_room(request: Request, room_id: int):
    if room_id not in room_pool:
        raise HTTPException(status_code=404, detail="Room not found")

    return get_template_response(
        request=request,
        name="game.html",
        context={"room_id": room_id},
    )
