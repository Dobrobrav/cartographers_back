from dataclasses import dataclass

from services.redis.redis_models_base import RedisModel


@dataclass
class RoomRedis(RedisModel):
    id: int
    name: str
    password: str
    max_users: int
    admin_id: int
    user_ids: list[int]
    current_users: int = 0
