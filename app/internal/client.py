from dataclasses import dataclass
from datetime import datetime

from fastapi import WebSocket

USER_COOKIE_KEY = "RUMMIKUB_USER_ID"


@dataclass()
class User:
    user_id: str
    nickname: str
    create_datetime: int
    last_datetime: int

    def __init__(self, user_id: str, nickname: str = ""):
        self.user_id = user_id
        self.nickname = nickname
        self.create_datetime = int(datetime.now().timestamp())
        self.last_datetime = self.create_datetime

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "nickname": self.nickname,
            "create_datetime": self.create_datetime,
            "last_datetime": self.last_datetime,
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
    play_user_count: int
    turn_time: int
    user_list: list[User]
    websocket_list: list[WebSocket]
    create_datetime: int
    last_datetime: int

    def __init__(
        self,
        room_id: str,
        play_user_count: int = 2,
        turn_time: int = 60,
        user_list: list[User] | None = None,
    ):
        if user_list is None:
            user_list = []

        self.room_id = room_id
        self.play_user_count = play_user_count
        self.turn_time = turn_time
        self.user_list = user_list
        self.websocket_list = []
        self.create_datetime = int(datetime.now().timestamp())
        self.last_datetime = self.create_datetime

    def to_dict(self) -> dict:
        return {
            "room_id": self.room_id,
            "play_user_count": self.play_user_count,
            "turn_time": self.turn_time,
            "user_list": [user.to_dict() for user in self.user_list],
            "websocket_count": len(self.websocket_list),
            "create_datetime": self.create_datetime,
            "last_datetime": self.last_datetime,
        }


class RoomManager:
    def __init__(self):
        self.room_dict: dict[str, Room] = {}  # {room_id: Room}

    def create_room(
        self,
        room_id: str,
        play_user_count: int,
        turn_time: int,
        user_list: list,
    ) -> Room:
        room = Room(
            room_id=room_id,
            play_user_count=play_user_count,
            turn_time=turn_time,
            user_list=user_list,
        )
        self.room_dict[room.room_id] = room
        return room

    def can_create_room(self, candidate_room_id: str) -> bool:
        candidate_room = Room(room_id=candidate_room_id)
        return not self.is_in_room_pool(room_id=candidate_room.room_id)

    def delete_room(self, room_id: str):
        try:
            room = self.get_room(room_id)
            del self.room_dict[room.room_id]
        except KeyError:
            pass

    def get_room(self, room_id: str) -> Room:
        if self.is_in_room_pool(room_id=room_id):
            return self.room_dict[room_id]
        raise KeyError(f"There is no room with room_id: {room_id}")

    def get_room_pool(self) -> list:
        return [room.to_dict() for room in self.room_dict.values()]

    def is_in_room_pool(self, room_id: str) -> bool:
        return room_id in self.room_dict

    # [COMMENT] User join
    def join_room(self, room_id: str, user: User):
        room = self.get_room(room_id)
        is_in_user = False
        for u in room.user_list:
            if u.user_id == user.user_id:
                is_in_user = True
        if not is_in_user:
            room.user_list.append(user)

    # [COMMENT] User leave
    def leave_room(self, room_id: str, user: User):
        room = self.get_room(room_id)
        for idx, u in enumerate(room.user_list):
            if u.user_id == user.user_id:
                del room.user_list[idx]

    # [COMMENT] WebSocket connect
    async def connect_room(self, room_id: str, websocket: WebSocket):
        room = self.get_room(room_id)
        await websocket.accept()
        room.websocket_list.append(websocket)

    # [COMMENT] WebSocket disconnect
    def disconnect_room(self, room_id: str, websocket: WebSocket):
        room = self.get_room(room_id)
        room.websocket_list.remove(websocket)

    # [COMMENT] WebSocket broadcast
    async def broadcast_room(self, room_id: str, message: str):
        room = self.get_room(room_id)
        for websocket in room.websocket_list:
            await websocket.send_text(message)


user_manager = UserManager()
room_manager = RoomManager()
