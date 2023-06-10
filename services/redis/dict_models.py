from services.redis.models_base import DictModel


class UserDict(DictModel):
    name: str
    is_ready: int
