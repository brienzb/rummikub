import random

from fastapi import APIRouter
from fastapi import Request, Response, Cookie

from app.internal.client import USER_KEY_NAME
from app.internal.client import user_manager as manager

user = APIRouter(
    prefix="/user",
    tags=["user"],
)


@user.post("/create")
async def create_user(
    request: Request,
    response: Response,
    rummikub_user_id: str = Cookie(default=None, alias=USER_KEY_NAME),
) -> dict:
    data = await request.body()
    nickname = data.decode("utf-8")

    if rummikub_user_id is not None:
        manager.delete_user(rummikub_user_id)

    while True:
        random_number = random.randint(10000, 99999)

        if manager.can_create_user(nickname, random_number):
            user_obj = manager.create_user(nickname, random_number)
            break

    response.set_cookie(key=USER_KEY_NAME, value=user_obj.user_id)
    print(f"[create_user] Create user_id: {user_obj.user_id}")
    return user_obj.to_dict()


@user.get("/list")
async def get_user_list(request: Request) -> list:
    return manager.get_user_list()
