from typing import Iterable

from django.contrib.auth.models import User

from services.redis.transformers_base import HashModel, DictModel, BaseFullTransformer
from services.redis.models_base import DataClassModel


class UserTransformer(BaseFullTransformer):

    @staticmethod
    def sql_model_to_dict_model(sql_model: User,
                                ) -> DictModel:
        dict_user = {
            "id": sql_model.id,
            'name': sql_model.username,
        }
        return dict_user

    @staticmethod
    def dc_model_to_dict_model(dc_model: DataClassModel,
                               ) -> DictModel:
        pass

    @staticmethod
    def hash_model_to_dc_model(hash_model: HashModel,
                               ) -> DataClassModel:
        pass
