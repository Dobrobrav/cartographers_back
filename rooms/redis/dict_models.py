from services.redis.models_base import DictModel


class RoomDict(DictModel):
    id: int
    name: str
    password: str
    max_users: int
    admin_id: int
    user_ids: list[int]
    current_users: int


class UserDict(DictModel):
    id: int
    name: str
