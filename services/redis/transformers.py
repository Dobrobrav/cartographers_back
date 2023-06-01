from typing import Iterable

from django.contrib.auth.models import User
from django.db.models import Model

from rooms.redis.dc_models import UserDC
from services.redis.dict_models import UserDict
from services.redis.transformers_base import HashModel, DictModel, BaseFullTransformer
from services.redis.models_base import DataClassModel


class UserTransformer(BaseFullTransformer):

    @staticmethod
    def sql_model_to_dc_model(sql_model: User,
                              ) -> UserDC:
        user_dc = UserDC(
            id=sql_model.pk,
            name=sql_model.username,
        )
        return user_dc

    @staticmethod
    def dc_model_to_dict_model(dc_model: UserDC,
                               ) -> DictModel:
        user_dict = UserDict(
            id=dc_model.id,
            name=dc_model.name,
        )
        return user_dict

    @staticmethod
    def hash_model_to_dc_model(hash_model: HashModel,
                               ) -> DataClassModel:
        pass
