import time
from datetime import datetime, timedelta

from app.internal.client import user_manager, room_manager

ALIVE_TIME = 3600
LOG_MESSAGE_TEMPLATE = """[monitor_client_alive_task | {DATETIME}]
    AS-IS
        - user_manger_count: {AS_IS_USER_MANAGER_COUNT}
        - room_manger_count: {AS_IS_ROOM_MANAGER_COUNT}
    TO-BE
        - user_manger_count: {TO_BE_USER_MANAGER_COUNT}
        - room_manger_count: {TO_BE_ROOM_MANAGER_COUNT}
    DELETED
        - user: {DELETED_USER_LIST}
        - room: {DELETED_ROOM_LIST}"""


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


def monitor_client_alive_task():
    while True:
        as_is_user_manager_count = len(user_manager.get_user_pool())
        as_is_room_manager_count = len(room_manager.get_room_pool())

        current_time = datetime.now()
        deleted_user_list = _clean_user_manager(current_time)
        deleted_room_list = _clean_room_manager(current_time)

        to_be_user_manager_count = len(user_manager.get_user_pool())
        to_be_room_manager_count = len(room_manager.get_room_pool())

        log_message = (
            LOG_MESSAGE_TEMPLATE.replace("{DATETIME}", str(current_time))
            .replace("{AS_IS_USER_MANAGER_COUNT}", str(as_is_user_manager_count))
            .replace("{AS_IS_ROOM_MANAGER_COUNT}", str(as_is_room_manager_count))
            .replace("{TO_BE_USER_MANAGER_COUNT}", str(to_be_user_manager_count))
            .replace("{TO_BE_ROOM_MANAGER_COUNT}", str(to_be_room_manager_count))
            .replace("{DELETED_USER_LIST}", str(deleted_user_list))
            .replace("{DELETED_ROOM_LIST}", str(deleted_room_list))
        )

        print(log_message)
        time.sleep(ALIVE_TIME)
