import hashlib
from dataclasses import dataclass
from datetime import datetime

from fastapi import WebSocket

USER_KEY_NAME = "RUMMIKUB_USER_ID"


@dataclass()
class User:
    user_id: str
    nickname: str
    random_number: int
    create_datetime: int

    def __init__(self, nickname: str, random_number: int):
        hash_key = f"{nickname}_{random_number}"
        self.user_id = hashlib.sha256(hash_key.encode("utf-8")).hexdigest()[:16]
        self.nickname = nickname
        self.random_number = random_number
        self.create_datetime = int(datetime.now().timestamp())

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "nickname": self.nickname,
            "random_number": self.random_number,
            "create_datetime": self.create_datetime,
        }


class UserManager:
    def __init__(self):
        self.user_dict: dict[str, User] = {}  # {user_id: User}

    def create_user(self, nickname: str, random_number: int) -> User:
        user = User(nickname=nickname, random_number=random_number)
        self.user_dict[user.user_id] = user
        return user

    def can_create_user(self, nickname: str, random_number: int) -> bool:
        user = User(nickname=nickname, random_number=random_number)
        return not self._is_in_user_list(user_id=user.user_id)

    def delete_user(self, user_id: str):
        try:
            user = self.get_user(user_id)
            del self.user_dict[user.user_id]
        except KeyError:
            pass

    def get_user(self, user_id: str) -> User:
        if self._is_in_user_list(user_id=user_id):
            return self.user_dict[user_id]
        raise KeyError(f"There is no user with user_id: {user_id}")

    def get_user_list(self) -> list:
        return [user.to_dict() for user in self.user_dict.values()]

    def _is_in_user_list(self, user_id: str) -> bool:
        return user_id in self.user_dict


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
client_manager = ClientManager()
