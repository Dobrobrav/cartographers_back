from abc import ABC
from dataclasses import dataclass


@dataclass
class RedisModel(ABC):
    id: int




