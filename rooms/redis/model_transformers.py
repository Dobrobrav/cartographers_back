from typing import Iterable

from django.db.models import Model

from rooms.redis.models import RoomRedis
from services.redis.model_transformers_base import ITransformer, ModelDict, ModelHash
from services.redis.redis_models_base import RedisModel


class RoomTransformer(ITransformer):
    @staticmethod
    def hashes_to_models(hashes: Iterable[ModelHash]) -> list[RedisModel]:
        pass

    @staticmethod
    def sql_model_to_dict(model: Model) -> ModelDict:
        pass

    @staticmethod
    def redis_model_to_dict(model: RoomRedis) -> ModelDict:
        hash = {
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
        return hash

    @staticmethod
    def hash_to_model(model_hash: ModelDict) -> RoomRedis:
        room = RoomRedis(
            id=int(model_hash['id']),
            name=model_hash['name'],
            password=model_hash['password'],
            max_users=int(model_hash['max_players']),
            admin_id=int(model_hash['admin_id']),
            user_ids=[
                int(user_id)
                for user_id in model_hash['user_ids'].split()
            ],
        )
        return room

    @staticmethod
    def bytes_to_redis_model(hash: ModelHash,
                             ) -> ModelDict:
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
