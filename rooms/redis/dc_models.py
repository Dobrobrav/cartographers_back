from dataclasses import dataclass
from typing import Optional

from services.redis.models_base import DataClassModel


@dataclass
class RoomDC(DataClassModel):
    name: str
    password: Optional[str]
    max_users: int
    admin_id: int
    user_ids: list[int]
    is_game_started: bool


@dataclass
class UserDC(DataClassModel):
    name: str
    is_ready: bool
