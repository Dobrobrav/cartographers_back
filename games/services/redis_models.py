from abc import ABC
from dataclasses import dataclass


class RedisModel(ABC):
    id: int


@dataclass
class MonsterCard(RedisModel):
    id: int
    name: str
    image_url: str
    shape: str
    exchange_order: str
