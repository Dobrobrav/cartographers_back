from typing import TypedDict, Sequence, MutableSequence

from services.redis.dict_models import UserPretty
from services.redis.models_base import DictModel, PrettyModel


class RoomDict(DictModel):
    name: str
    password: str
    max_users: int
    admin_id: int
    user_ids: str
    is_game_started: str  # true or false
    # is_ready_for_game: str  # true or false


class RoomPretty(PrettyModel):
    id: int
    name: str
    password: str | None
    max_users: int
    admin_id: int
    user_ids: Sequence[int]
    is_game_started: bool
    is_ready_for_game: bool
    users: Sequence[UserPretty]


class RoomPrettyForPage(TypedDict):
    """ not derived from DictModel """
    id: int
    name: str
    max_users: int
    current_users: int
    contains_password: bool
    is_game_started: bool
