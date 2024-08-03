from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request, Cookie

from app.internal.client import USER_COOKIE_KEY
from app.internal.client import user_manager, room_manager
from app.internal.template import get_template_response
from app.internal.util import generate_random_string

room = APIRouter(
    prefix="/room",
    tags=["room"],
)


def check_user_alive(user_id: str | None) -> bool:
    if user_id is None:
        return False
    return user_manager.is_in_user_pool(user_id)


@room.post("/create")
async def create_room(
    request: Request,
    rummikub_user_id: str = Cookie(default=None, alias=USER_COOKIE_KEY),
) -> str:
    if not check_user_alive(rummikub_user_id):
        raise HTTPException(status_code=403, detail="Create a user first")
    user_obj = user_manager.get_user(rummikub_user_id)

    while True:
        room_id = generate_random_string()

        if room_manager.can_create_room(room_id):
            room_obj = room_manager.create_room(room_id=room_id, user_list=[user_obj])
            break

    print(f"[create_room] Create room_id: {room_obj.room_id}")
    return room_id


@room.get("/{room_id}")
async def get_room(
    request: Request,
    room_id: str,
    rummikub_user_id: str = Cookie(default=None, alias=USER_COOKIE_KEY),
):
    if not room_manager.is_in_room_pool(room_id):
        raise HTTPException(status_code=404, detail="Room not found")

    if not check_user_alive(rummikub_user_id):
        raise HTTPException(status_code=403, detail="Create a user first")

    # TODO: URL 치고 입력한 사람은 입장 불가 (room.user_list 안에 존재하는 user 인지 확인)

    return get_template_response(
        request=request,
        name="game.html",
        context={"room_id": room_id},
    )


# [ADMIN] Room 풀 확인용 API
@room.get("/get/pool")
async def get_room_pool(request: Request) -> list:
    return room_manager.get_room_pool()
