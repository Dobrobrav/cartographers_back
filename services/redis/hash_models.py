from services.redis.base.models_base import HashModel


class UserHash(HashModel):
    name: bytes
    is_ready: bytes
