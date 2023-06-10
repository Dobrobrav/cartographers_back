from services.redis.models_base import HashModel


class UserHash(HashModel):
    name: bytes
    is_ready: bytes
