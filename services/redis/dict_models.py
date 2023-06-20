from typing import TypedDict

from services.redis.base.models_base import DictModel


class UserDict(DictModel):
    name: str
    is_ready: str  # true or false


class UserPretty(TypedDict):
    id: int
    name: str
    is_ready: bool