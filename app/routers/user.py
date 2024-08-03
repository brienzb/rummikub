from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request, Response, Cookie

from app.internal.client import USER_COOKIE_KEY
from app.internal.client import user_manager
from app.internal.util import generate_random_string

user = APIRouter(
    prefix="/user",
    tags=["user"],
)


@user.post("/create")
async def create_user(
    request: Request,
    response: Response,
    rummikub_user_id: str = Cookie(default=None, alias=USER_COOKIE_KEY),
) -> dict:
    data = await request.body()
    nickname = data.decode("utf-8")

    if rummikub_user_id is not None:
        user_manager.delete_user(rummikub_user_id)

    while True:
        user_id = generate_random_string()

        if user_manager.can_create_user(user_id):
            user_obj = user_manager.create_user(user_id=user_id, nickname=nickname)
            break

    response.set_cookie(key=USER_COOKIE_KEY, value=user_obj.user_id)
    print(f"[create_user] Create user_id: {user_obj.user_id}")
    return user_obj.to_dict()


@user.get("/get")
async def get_user(
    request: Request,
    rummikub_user_id: str = Cookie(default=None, alias=USER_COOKIE_KEY),
) -> dict:
    try:
        return user_manager.get_user(rummikub_user_id).to_dict()
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")


# [ADMIN] User 풀 확인용 API
@user.get("/get/pool")
async def get_user_pool(request: Request) -> list:
    return user_manager.get_user_pool()
