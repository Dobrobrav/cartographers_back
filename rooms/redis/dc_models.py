from dataclasses import dataclass
from typing import Optional, MutableSequence

from services.redis.base.models_base import DataClassModel


@dataclass
class RoomDC(DataClassModel):
    name: str
    password: Optional[str]
    max_users: int
    admin_id: int
    user_ids: MutableSequence[int]
    is_game_started: bool
    # is_ready_for_game: bool


@dataclass
class UserDC(DataClassModel):
    name: str
    is_ready: bool
