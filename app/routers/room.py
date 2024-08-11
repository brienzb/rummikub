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


def check_room_alive(room_id: str) -> bool:
    return room_manager.is_in_room_pool(room_id)


@room.post("/create")
async def create_room(
    request: Request,
    rummikub_user_id: str = Cookie(default=None, alias=USER_COOKIE_KEY),
) -> str:
    if not check_user_alive(rummikub_user_id):
        raise HTTPException(status_code=403, detail="Create a user first")
    this_user = user_manager.get_user(rummikub_user_id)

    while True:
        room_id = generate_random_string()

        if room_manager.can_create_room(room_id):
            this_room = room_manager.create_room(room_id=room_id, user_list=[this_user])
            break

    print(f"[create_room] Create room_id: {this_room.room_id}")
    return room_id


@room.post("/join")
async def join_room(
    request: Request,
    rummikub_user_id: str = Cookie(default=None, alias=USER_COOKIE_KEY),
):
    data = await request.body()
    room_id = data.decode("utf-8")

    if not check_user_alive(rummikub_user_id):
        raise HTTPException(status_code=403, detail="Create a user first")
    this_user = user_manager.get_user(rummikub_user_id)

    if not check_room_alive(room_id):
        raise HTTPException(status_code=404, detail="Room not found")
    this_room = room_manager.get_room(room_id)

    this_room.user_list.append(this_user)


@room.get("/{room_id}")
async def get_room(
    request: Request,
    room_id: str,
    rummikub_user_id: str = Cookie(default=None, alias=USER_COOKIE_KEY),
):
    if not check_user_alive(rummikub_user_id):
        raise HTTPException(status_code=403, detail="Create a user first")
    this_user = user_manager.get_user(rummikub_user_id)

    if not check_room_alive(room_id):
        raise HTTPException(status_code=404, detail="Room not found")
    this_room = room_manager.get_room(room_id)

    # [COMMENT] 참여 권한 있는 user 인지 확인
    id_valid_user = False
    for user in this_room.user_list:
        if user.user_id == this_user.user_id:
            id_valid_user = True
    if not id_valid_user:
        raise HTTPException(status_code=401, detail="No permission to join in the room")

    return get_template_response(
        request=request,
        name="game.html",
        context={"room_id": room_id},
    )


# [ADMIN] room 풀 확인용 API
@room.get("/get/pool")
async def get_room_pool(request: Request) -> list:
    return room_manager.get_room_pool()
