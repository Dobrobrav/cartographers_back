from typing import Iterable

from django.contrib.auth.models import User
from django.db.models import Model

from services.redis.model_transformers_base import BaseRedisTransformer, HashModel, DictModel
from services.redis.redis_models_base import DataClassModel


class UserTransformer(BaseRedisTransformer):
    def sql_models_to_dict_models(self,
                                  models: Iterable[User],
                                  ) -> list[DictModel]:
        dict_users = [
            self.sql_model_to_dict_model(model)
            for model in models
        ]
        return dict_users

    @staticmethod
    def dc_models_to_dict_models(dc_model: Iterable[DataClassModel]) -> list[DictModel]:
        pass

    @staticmethod
    def hash_models_to_dc_models(hash_models: Iterable[HashModel]) -> list[DataClassModel]:
        pass

    @staticmethod
    def sql_model_to_dict_model(sql_model: User) -> DictModel:
        dict_user = {
            "id": sql_model.id,
            'name': sql_model.username,
        }
        return dict_user

    @staticmethod
    def dc_model_to_dict_model(dc_model: DataClassModel) -> DictModel:
        pass

    @staticmethod
    def hash_model_to_dc_model(hash_model: HashModel) -> DataClassModel:
        pass

    @staticmethod
    def hashes_to_models(hashes: Iterable[HashModel]) -> list[DataClassModel]:
        pass
