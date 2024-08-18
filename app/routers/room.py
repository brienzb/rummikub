import json

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request, Cookie
from fastapi import status

from app.internal.client import USER_COOKIE_KEY
from app.internal.client import User, Room
from app.internal.client import user_manager, room_manager
from app.internal.template import get_template_response
from app.internal.util import generate_random_string
from app.internal.util import is_alive_user, is_alive_room
from app.internal.util import print_log

room = APIRouter(
    prefix="/room",
    tags=["room"],
)


def get_this_user(user_id: str | None) -> User:
    if not is_alive_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Create a user first",
        )
    return user_manager.get_user(user_id)


def get_this_room(room_id: str | None) -> Room:
    if not is_alive_room(room_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )
    return room_manager.get_room(room_id)


@room.post("/create")
async def create_room(
    request: Request,
    rummikub_user_id: str = Cookie(default=None, alias=USER_COOKIE_KEY),
) -> str:
    data = await request.body()
    room_info = json.loads(data.decode("utf-8"))

    this_user = get_this_user(rummikub_user_id)

    while True:
        room_id = generate_random_string()

        if room_manager.can_create_room(room_id):
            this_room = room_manager.create_room(
                room_id=room_id,
                play_user_count=room_info["playUserCount"],
                turn_time=room_info["turnTime"],
                user_list=[this_user],
            )
            break

    print_log("create_room", f"Create room_id: {this_room.room_id}")
    return room_id


@room.post("/join")
async def join_room(
    request: Request,
    rummikub_user_id: str = Cookie(default=None, alias=USER_COOKIE_KEY),
):
    data = await request.body()
    room_id = data.decode("utf-8")

    this_user = get_this_user(rummikub_user_id)
    this_room = get_this_room(room_id)

    room_manager.join_room(room_id=this_room.room_id, user=this_user)


@room.get("/{room_id}")
async def get_room(
    request: Request,
    room_id: str,
    rummikub_user_id: str = Cookie(default=None, alias=USER_COOKIE_KEY),
):
    this_user = get_this_user(rummikub_user_id)
    this_room = get_this_room(room_id)

    # [COMMENT] 참여 권한 있는 user 인지 확인
    id_valid_user = False
    for user in this_room.user_list:
        if user.user_id == this_user.user_id:
            id_valid_user = True
    if not id_valid_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No permission to join in the room",
        )

    return get_template_response(
        request=request,
        name="game.html",
        context={"room_id": room_id},
    )


# [ADMIN] room 풀 확인용 API
@room.get("/get/pool", tags=["admin"])
async def get_room_pool(request: Request) -> list:
    return room_manager.get_room_pool()
