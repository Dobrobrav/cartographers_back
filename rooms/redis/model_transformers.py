from typing import Iterable

from django.db.models import Model

from rooms.redis.models import RoomRedis
from services.redis.model_transformers_base import BaseModelTransformer, DictModel, HashModel
from services.redis.redis_models_base import RedisModel


class RoomTransformer(BaseModelTransformer):
    @staticmethod
    def sql_model_to_dict_model(model: Model) -> DictModel:
        pass

    @staticmethod
    def redis_model_to_dict_model(model: RoomRedis,
                                  ) -> DictModel:
        model_dict = {
            'id': model.id,
            'name': model.name,
            'password': model.password,
            'max_players': model.max_users,
            'admin_id': model.admin_id,
            'user_ids': ' '.join(
                str(user_id)
                for user_id in model.user_ids
            ),
        }
        return model_dict

    @staticmethod
    def hash_model_to_redis_model(hash_model: HashModel) -> RoomRedis:
        redis_model = RoomRedis(
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
