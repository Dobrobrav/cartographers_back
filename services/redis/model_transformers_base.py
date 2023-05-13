from abc import ABC, abstractmethod
from typing import TypeAlias, Iterable

from django.db.models import Model

from services.redis.redis_models_base import RedisModel

ModelDict: TypeAlias = dict[str, str | int]
ModelHash: TypeAlias = dict[bytes, bytes]


class ITransformer(ABC):  # Нужен ли этот интерфейс вообще?
    @staticmethod
    @abstractmethod
    def sql_model_to_dict(model: Model) -> ModelDict:
        pass

    @staticmethod
    @abstractmethod
    def redis_model_to_dict(model: RedisModel) -> ModelDict:
        pass

    @staticmethod
    @abstractmethod
    def hash_to_model(hash: ModelHash) -> RedisModel:
        pass

    @staticmethod
    @abstractmethod
    def hashes_to_models(hashes: Iterable[ModelHash],
                         ) -> list[RedisModel]:
        pass
