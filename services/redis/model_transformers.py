from typing import Iterable

from django.db.models import Model

from services.redis.model_transformers_base import BaseModelTransformer, HashModel, DictModel
from services.redis.redis_models_base import RedisModel


class UserTransformer(BaseModelTransformer):
    @staticmethod
    def sql_models_to_dict_models(models: Iterable[Model]) -> list[DictModel]:
        pass

    @staticmethod
    def redis_models_to_dict_models(models: Iterable[RedisModel]) -> list[DictModel]:
        pass

    @staticmethod
    def hash_models_to_redis_models(models: Iterable[HashModel]) -> list[RedisModel]:
        pass

    @staticmethod
    def sql_model_to_dict_model(model: Model) -> DictModel:
        pass

    @staticmethod
    def redis_model_to_dict_model(model: RedisModel) -> DictModel:
        pass

    @staticmethod
    def hash_model_to_redis_model(hash: HashModel) -> RedisModel:
        pass

    @staticmethod
    def hashes_to_models(hashes: Iterable[HashModel]) -> list[RedisModel]:
        pass
