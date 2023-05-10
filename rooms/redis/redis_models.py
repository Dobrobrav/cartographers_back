from dataclasses import dataclass

from services.redis_models_base import RedisModel


@dataclass
class RoomRedis(RedisModel):
    id: int
    name: str
    password: str
    max_players: int
    admin_id: int
