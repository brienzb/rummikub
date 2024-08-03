import random

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request, Cookie

from app.internal.client import USER_COOKIE_KEY
from app.internal.client import user_manager
from app.internal.templates import get_template_response

room = APIRouter(
    prefix="/room",
    tags=["room"],
)


# TODO: room_pool 싱글톤 객체로 구현 (혹은 다른 무언가..)
room_pool = []


def check_user_alive(user_id: str | None) -> bool:
    if user_id is None:
        return False
    return user_manager.is_in_user_pool(user_id)


@room.post("/create")
async def create_room(
    request: Request,
    rummikub_user_id: str = Cookie(default=None, alias=USER_COOKIE_KEY),
) -> int:
    if not check_user_alive(rummikub_user_id):
        raise HTTPException(status_code=403, detail="Create a user first")

    # TODO: room_id 생성 로직 구현
    room_id = random.randint(10000, 99999)

    room_pool.append(room_id)
    print("current room pool status:", room_pool)

    return room_id


@room.get("/{room_id}")
async def get_room(
    request: Request,
    room_id: int,
    rummikub_user_id: str = Cookie(default=None, alias=USER_COOKIE_KEY),
):
    if room_id not in room_pool:
        raise HTTPException(status_code=404, detail="Room not found")

    if not check_user_alive(rummikub_user_id):
        raise HTTPException(status_code=403, detail="Create a user first")

    return get_template_response(
        request=request,
        name="game.html",
        context={"room_id": room_id},
    )
