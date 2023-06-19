from typing import Iterable

from django.contrib.auth.models import User

from rooms.redis.dc_models import UserDC
from services.redis.dict_models import UserDict, UserPretty
from services.redis.hash_models import UserHash
from services.redis.transformers_base import DictModel, BaseFullTransformer
from services.utils import serialize, decode_bytes, deserialize


class UserTransformer(BaseFullTransformer):

    @staticmethod
    def sql_model_to_dc_model(sql_model: User,
                              readiness_status: bool,
                              ) -> UserDC:
        user_dc = UserDC(
            id=sql_model.pk,
            name=sql_model.username,
            is_ready=readiness_status,
        )
        return user_dc

    @staticmethod
    def dc_model_to_dict_model(dc_model: UserDC,
                               ) -> UserDict:
        user_dict = UserDict(
            id=dc_model.id,
            name=dc_model.name,
            is_ready=serialize(dc_model.is_ready)
        )
        return user_dict

    @staticmethod
    def hash_model_to_dc_model(hash_model: UserHash,
                               ) -> UserDC:
        user_dc = UserDC(
            id=int(hash_model[b'id']),
            name=decode_bytes(hash_model[b'name']),
            is_ready=deserialize(hash_model[b'is_ready']),
        )
        return user_dc

    @staticmethod
    def dc_model_to_model_pretty(user_dc: UserDC,
                                 ) -> UserPretty:
        user_pretty = UserPretty(
            id=user_dc.id,
            name=user_dc.name,
            is_ready=user_dc.is_ready,
        )
        return user_pretty

    def sql_users_to_pretty_users(self,
                                  sql_models: Iterable[User],
                                  readiness_statuses: Iterable[bool],
                                  ) -> list[UserPretty]:
        users_pretty = [
            self.sql_model_to_pretty_model(sql_model, status)
            for sql_model, status in zip(sql_models, readiness_statuses)
        ]
        return users_pretty

    def sql_model_to_pretty_model(self,
                                  sql_model: User,
                                  readiness_status: bool,
                                  ) -> UserPretty:
        user_dc = self.sql_model_to_dc_model(sql_model, readiness_status)
        user_pretty = self.dc_model_to_model_pretty(user_dc)
        return user_pretty
