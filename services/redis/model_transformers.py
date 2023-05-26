from typing import Iterable

from django.contrib.auth.models import User
from django.db.models import Model

from services.redis.model_transformers_base import BaseModelTransformer, HashModel, DictModel
from services.redis.redis_models_base import RedisModel


class UserTransformer(BaseModelTransformer):
    def sql_models_to_dict_models(self,
                                  models: Iterable[User],
                                  ) -> list[DictModel]:
        dict_users = [
            self.sql_model_to_dict_model(model)
            for model in models
        ]
        return dict_users

    @staticmethod
    def redis_models_to_dict_models(models: Iterable[RedisModel]) -> list[DictModel]:
        pass

    @staticmethod
    def hash_models_to_redis_models(models: Iterable[HashModel]) -> list[RedisModel]:
        pass

    @staticmethod
    def sql_model_to_dict_model(model: User) -> DictModel:
        dict_user = {
            "id": model.id,
            'name': model.username,
        }
        return dict_user

    @staticmethod
    def redis_model_to_dict_model(model: RedisModel) -> DictModel:
        pass

    @staticmethod
    def hash_model_to_redis_model(hash: HashModel) -> RedisModel:
        pass

    @staticmethod
    def hashes_to_models(hashes: Iterable[HashModel]) -> list[RedisModel]:
        pass
