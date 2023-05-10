from abc import ABC, abstractmethod
from typing import TypeAlias

from django.db.models import Model

from services.redis_models_base import RedisModel

ModelHash: TypeAlias = dict[str, str]


class ITransformer(ABC):
    @staticmethod
    @abstractmethod
    def dump_sql_model(model: Model) -> ModelHash:
        pass

    @staticmethod
    @abstractmethod
    def dump_redis_model(model: RedisModel) -> ModelHash:
        pass

    @staticmethod
    @abstractmethod
    def load_redis_model(redis_hash: ModelHash) -> RedisModel:
        pass




