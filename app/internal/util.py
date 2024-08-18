import random
import string

from app.internal.client import user_manager, room_manager

RANDOM_STRING_LENGTH = 16


def generate_random_string(length: int = RANDOM_STRING_LENGTH):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


def is_alive_user(user_id: str | None) -> bool:
    if user_id is None:
        return False
    return user_manager.is_in_user_pool(user_id)


def is_alive_room(room_id: str | None) -> bool:
    if room_id is None:
        return False
    return room_manager.is_in_room_pool(room_id)


def refresh_alive_user(user_id: str):
    user_manager.refresh_user(user_id)


def refresh_alive_room(room_id: str):
    room_manager.refresh_room(room_id)
