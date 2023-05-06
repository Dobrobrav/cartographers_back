from typing import Iterable

from redis.client import Redis
from .key_schemas import KeySchema
from abc import ABC, abstractmethod

from .model_transformers import ModelTransformer
from .redis_models import RedisModel


class DaoBase(ABC):
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


class RedisDaoInit:
    _redis: Redis
    _key_schema: KeySchema
    _transformer: ModelTransformer

    def __init__(self,
                 redis_client: Redis,
                 key_schema: KeySchema,
                 model_transformer: ModelTransformer,
                 ) -> None:
        self._redis = redis_client
        self._key_schema = key_schema
        self._transformer = model_transformer
