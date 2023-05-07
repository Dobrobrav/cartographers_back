from typing import Iterable

from redis.client import Redis
from .key_schemas import KeySchema
from abc import ABC, abstractmethod

from .model_transformers import ModelTransformer
from .redis_models import RedisModel


class Dao(ABC):
    _key_schema: KeySchema
    _transformer: ModelTransformer

    @abstractmethod
    def insert(self, redis_model: RedisModel) -> None:
        pass

    @abstractmethod
    def insert_many(self, redis_models: Iterable[RedisModel]) -> None:
        pass

    @abstractmethod
    def fetch_by_id(self, model_id: int) -> RedisModel:
        pass

    @abstractmethod
    def fetch_all(self) -> set[RedisModel]:
        pass

