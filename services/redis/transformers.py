from django.contrib.auth.models import User

from rooms.redis.dc_models import UserDC
from services.redis.dict_models import UserDict
from services.redis.hash_models import UserHash
from services.redis.transformers_base import DictModel, BaseFullTransformer


class UserTransformer(BaseFullTransformer):

    @staticmethod
    def sql_model_to_dc_model(sql_model: User,
                              ) -> UserDC:
        user_dc = UserDC(
            id=sql_model.pk,
            name=sql_model.username,
            is_ready=False,
        )
        return user_dc

    @staticmethod
    def dc_model_to_dict_model(dc_model: UserDC,
                               ) -> DictModel:
        user_dict = UserDict(
            id=dc_model.id,
            name=dc_model.name,
            is_ready=int(dc_model.is_ready)
        )
        return user_dict

    @staticmethod
    def hash_model_to_dc_model(hash_model: UserHash,
                               ) -> UserDC:
        user_dc = UserDC(
            id=int(hash_model[b'id']),
            name=hash_model[b'id'].decode('utf-8'),
            is_ready=bool(int(hash_model[b'is_ready']))
        )
        return user_dc
