from abc import ABC, abstractmethod
from typing import TypeAlias

from games.services.redis_models import RedisModel

ModelHash: TypeAlias = dict[str, str]


class ModelTransformer(ABC):
    @abstractmethod
    def dump(self,
             model: RedisModel,
             ) -> ModelHash:
        pass

    @abstractmethod
    def load(self,
             redis_hash: ModelHash,
             ) -> RedisModel:
        pass
