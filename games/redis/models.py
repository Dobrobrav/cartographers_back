from dataclasses import dataclass
from services.redis.redis_models_base import RedisModel


@dataclass
class MonsterCardRedis(RedisModel):
    id: int
    name: str
    image_url: str
    shape: str
    exchange_order: str
