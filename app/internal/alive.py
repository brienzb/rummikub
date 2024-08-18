import json
import time
from datetime import datetime, timedelta

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.internal.client import USER_COOKIE_KEY
from app.internal.client import user_manager, room_manager
from app.internal.util import print_log
from app.internal.util import is_alive_user, is_alive_room
from app.internal.util import refresh_alive_user, refresh_alive_room

ALIVE_TIME = 3600  # [COMMENT] 1시간(3600초) 기준 alive 확인
CLEAN_CLIENT_LOG_MESSAGE_TEMPLATE = """
    AS-IS
        - user_manger_count: {AS_IS_USER_MANAGER_COUNT}
        - room_manger_count: {AS_IS_ROOM_MANAGER_COUNT}
    TO-BE
        - user_manger_count: {TO_BE_USER_MANAGER_COUNT}
        - room_manger_count: {TO_BE_ROOM_MANAGER_COUNT}
    DELETED
        - user: {DELETED_USER_LIST}
        - room: {DELETED_ROOM_LIST}
"""


def _clean_user_manager(check_datetime: datetime) -> list:
    user_pool = user_manager.get_user_pool()

    user_to_be_deleted_list = []
    for user in user_pool:
        user_last_datetime = datetime.fromtimestamp(user["last_datetime"])

        time_difference = abs(check_datetime - user_last_datetime)
        if time_difference > timedelta(seconds=ALIVE_TIME):
            user_to_be_deleted_list.append(user)

    for user in user_to_be_deleted_list:
        user_manager.delete_user(user["user_id"])

    return user_to_be_deleted_list


def _clean_room_manager(check_datetime: datetime) -> list:
    room_pool = room_manager.get_room_pool()

    room_to_be_deleted_list = []
    for room in room_pool:
        room_last_datetime = datetime.fromtimestamp(room["last_datetime"])

        time_difference = abs(check_datetime - room_last_datetime)
        if time_difference > timedelta(seconds=ALIVE_TIME):
            room_to_be_deleted_list.append(room)

    for room in room_to_be_deleted_list:
        room_manager.delete_room(room["room_id"])

    return room_to_be_deleted_list


def clean_client_task():
    while True:
        as_is_user_manager_count = len(user_manager.get_user_pool())
        as_is_room_manager_count = len(room_manager.get_room_pool())

        current_time = datetime.now()
        deleted_user_list = _clean_user_manager(current_time)
        deleted_room_list = _clean_room_manager(current_time)

        to_be_user_manager_count = len(user_manager.get_user_pool())
        to_be_room_manager_count = len(room_manager.get_room_pool())

        # fmt: off
        log_message = (
            CLEAN_CLIENT_LOG_MESSAGE_TEMPLATE
            .replace("{AS_IS_USER_MANAGER_COUNT}", str(as_is_user_manager_count))
            .replace("{AS_IS_ROOM_MANAGER_COUNT}", str(as_is_room_manager_count))
            .replace("{TO_BE_USER_MANAGER_COUNT}", str(to_be_user_manager_count))
            .replace("{TO_BE_ROOM_MANAGER_COUNT}", str(to_be_room_manager_count))
            .replace("{DELETED_USER_LIST}", str(deleted_user_list))
            .replace("{DELETED_ROOM_LIST}", str(deleted_room_list))
        )
        # fmt: on

        print_log("clean_client_task", log_message)
        time.sleep(ALIVE_TIME)


class RefreshAliveMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if (
            request.url.path == "/"
            or request.url.path.startswith("/static")
            or request.url.path.startswith("/user/create")
            or request.url.path.startswith("/room/create")
            or request.url.path.startswith("/user/get/pool")  # [COMMENT] ADMIN API
            or request.url.path.startswith("/room/get/pool")  # [COMMENT] ADMIN API
        ):
            return await call_next(request)

        # [COMMENT] cookie 값 확인해, user_id refresh
        user_id = request.cookies.get(USER_COOKIE_KEY)
        if is_alive_user(user_id):
            refresh_alive_user(user_id)

        # [COMMENT] path 값 확인해, room_id refresh
        path_room_id, path_params = None, request.url.path
        if path_params.startswith("/room/"):
            path_room_id = path_params.split("/")[1]
            if is_alive_room(path_room_id):
                refresh_alive_room(path_room_id)

        # [COMMENT] data 값 확인해, room_id refresh
        data = await request.body()
        data_room_id, content = None, data.decode("utf-8")
        try:
            content = json.loads(content)
            data_room_id = content["roomId"]
        except Exception:
            data_room_id = content
        finally:
            if is_alive_room(data_room_id):
                refresh_alive_room(data_room_id)

        print_log(
            "RefreshAliveMiddleware",
            f"user_id: {user_id}, path_room_id: {path_room_id}, data_room_id: {data_room_id}",
        )
        return await call_next(request)
