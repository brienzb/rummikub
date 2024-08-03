from dataclasses import dataclass
from datetime import datetime

from fastapi import WebSocket

USER_COOKIE_KEY = "RUMMIKUB_USER_ID"


@dataclass()
class User:
    user_id: str
    nickname: str
    create_datetime: int

    def __init__(self, user_id: str, nickname: str = ""):
        self.user_id = user_id
        self.nickname = nickname
        self.create_datetime = int(datetime.now().timestamp())

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "nickname": self.nickname,
            "create_datetime": self.create_datetime,
        }


class UserManager:
    def __init__(self):
        self.user_dict: dict[str, User] = {}  # {user_id: User}

    def create_user(self, user_id: str, nickname: str) -> User:
        user = User(user_id=user_id, nickname=nickname)
        self.user_dict[user.user_id] = user
        return user

    def can_create_user(self, candidate_user_id: str) -> bool:
        candidate_user = User(user_id=candidate_user_id)
        return not self.is_in_user_pool(user_id=candidate_user.user_id)

    def delete_user(self, user_id: str):
        try:
            user = self.get_user(user_id)
            del self.user_dict[user.user_id]
        except KeyError:
            pass

    def get_user(self, user_id: str) -> User:
        if self.is_in_user_pool(user_id=user_id):
            return self.user_dict[user_id]
        raise KeyError(f"There is no user with user_id: {user_id}")

    def get_user_pool(self) -> list:
        return [user.to_dict() for user in self.user_dict.values()]

    def is_in_user_pool(self, user_id: str) -> bool:
        return user_id in self.user_dict


@dataclass()
class Room:
    room_id: str
    user_list: list[User]
    websocket: WebSocket
    create_datetime: int

    def __init__(self, room_id: str, user_list: list[User] | None = None):
        if user_list is None:
            user_list = []

        self.room_id = room_id
        self.user_list = user_list
        self.create_datetime = int(datetime.now().timestamp())

    def to_dict(self) -> dict:
        return {
            "room_id": self.room_id,
            "user_list": [user.to_dict() for user in self.user_list],
            "create_datetime": self.create_datetime,
        }


class RoomManager:
    def __init__(self):
        self.room_dict: dict[str, Room] = {}  # {room_id: Room}

    def create_room(self, room_id: str, user_list: list) -> Room:
        room = Room(room_id=room_id, user_list=user_list)
        self.room_dict[room.room_id] = room
        return room

    def can_create_room(self, candidate_room_id: str) -> bool:
        candidate_room = Room(room_id=candidate_room_id)
        return not self.is_in_room_pool(room_id=candidate_room.room_id)

    def get_room_pool(self) -> list:
        return [room.to_dict() for room in self.room_dict.values()]

    def is_in_room_pool(self, room_id: str) -> bool:
        return room_id in self.room_dict


# TODO: WebSocket 매니저 로직 수정 필요
class ClientManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


user_manager = UserManager()
room_manager = RoomManager()
client_manager = ClientManager()
