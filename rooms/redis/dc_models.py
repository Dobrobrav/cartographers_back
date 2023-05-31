from dataclasses import dataclass

from services.redis.models_base import DataClassModel


@dataclass
class RoomDC(DataClassModel):
    id: int
    name: str
    password: str
    max_users: int
    admin_id: int
    user_ids: list[int]
    current_users: int = 0


@dataclass
class UserDC(DataClassModel):
    id: int
    name: str
