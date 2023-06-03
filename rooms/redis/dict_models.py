from typing import TypedDict

from services.redis.models_base import DictModel


class RoomDict(DictModel):
    name: str
    password: str
    max_users: int
    admin_id: int
    user_ids: str
    is_game_started: int


# special case
class RoomDictForPage(TypedDict):
    """ not derived from DictModel """
    room_id: int
    room_name: str
    max_users: int
    current_users: int
    contains_password: bool
    is_game_started: bool
