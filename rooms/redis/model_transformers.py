from typing import Iterable

from django.db.models import Model

from rooms.redis.models import RoomDC
from services.redis.model_transformers_base import BaseRedisTransformer, DictModel, HashModel
from services.redis.redis_models_base import DataClassModel


class RoomTransformer(BaseRedisTransformer):
    @staticmethod
    def sql_model_to_dict_model(sql_model: Model) -> DictModel:
        pass

    @staticmethod
    def dc_model_to_dict_model(dc_model: RoomDC,
                               ) -> DictModel:
        model_dict = {
            'id': dc_model.id,
            'name': dc_model.name,
            'password': dc_model.password,
            'max_players': dc_model.max_users,
            'admin_id': dc_model.admin_id,
            'user_ids': ' '.join(
                str(user_id)
                for user_id in dc_model.user_ids
            ),
        }
        return model_dict

    @staticmethod
    def hash_model_to_dc_model(hash_model: HashModel) -> RoomDC:
        redis_model = RoomDC(
            id=int(hash_model[b'id']),
            name=hash_model[b'name'].decode('utf-8'),
            password=hash_model[b'password'].decode('utf-8'),
            max_users=int(hash_model[b'max_players']),
            admin_id=int(hash_model[b'admin_id']),
            user_ids=[
                int(user_id)
                for user_id in hash_model[b'user_ids'].split()
            ],
        )

        return redis_model

    @staticmethod
    def bytes_to_redis_model(hash: HashModel,
                             ) -> DictModel:
        room_hash = {
            'id': int(hash[b'id']),
            'name': hash[b'name'],
            'password': hash[b'password'],
            'max_players': int(hash[b'max_players']),
            'admin_id': int(hash[b'admin_id']),
            'user_ids': [
                int(user_id)
                for user_id in hash[b'user_ids'].split()
            ],
        }
        return room_hash
