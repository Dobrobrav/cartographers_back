from services.redis.models_base import DictModel


class UserDict(DictModel):
    id: int
    name: str
