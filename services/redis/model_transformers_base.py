from abc import ABC, abstractmethod
from typing import TypeAlias, Iterable, Any

from django.db.models import Model

from services.redis.redis_models_base import RedisModel

DictModel: TypeAlias = dict[str, Any]
HashModel: TypeAlias = dict[bytes, bytes]


class BaseModelTransformer(ABC):
    def sql_models_to_dict_models(self,
                                  models: Iterable[Model],
                                  ) -> list[DictModel]:
        dict_models = [
            self.sql_model_to_dict_model(model)
            for model in models
        ]
        return dict_models

    @staticmethod
    @abstractmethod
    def sql_model_to_dict_model(model: Model,
                                ) -> DictModel:
        pass

    # @staticmethod
    # @abstractmethod
    # def redis_models_to_dict_models(models: Iterable[RedisModel],
    #                                 ) -> list[DictModel]:
    #     pass

    def redis_models_to_dict_models(self,
                                    models: Iterable[RedisModel],
                                    ) -> list[DictModel]:
        dict_models = [
            self.redis_model_to_dict_model(model)
            for model in models
        ]
        return dict_models

    @staticmethod
    @abstractmethod
    def redis_model_to_dict_model(model: RedisModel,
                                  ) -> DictModel:
        pass

    # @staticmethod
    # @abstractmethod
    # def hash_models_to_redis_models(models: Iterable[HashModel],
    #                                 ) -> list[RedisModel]:
    #     pass

    def hash_models_to_redis_models(self,
                                    models: Iterable[HashModel],
                                    ) -> list[RedisModel]:
        redis_models = [
            self.hash_model_to_redis_model(model)
            for model in models
        ]
        return redis_models

    @staticmethod
    @abstractmethod
    def hash_model_to_redis_model(hash: HashModel,
                                  ) -> RedisModel:
        pass

    def hash_model_to_dict_model(self,
                                 hash_model: HashModel,
                                 ) -> DictModel:
        redis_model = self.hash_model_to_redis_model(hash_model)
        dict_model = self.redis_model_to_dict_model(redis_model)

        return dict_model
