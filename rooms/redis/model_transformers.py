from typing import Iterable

from django.db.models import Model

from rooms.redis.models import RoomRedis
from services.redis.model_transformers_base import BaseModelTransformer, DictModel, HashModel
from services.redis.redis_models_base import RedisModel


class RoomTransformer(BaseModelTransformer):
    @staticmethod
    def sql_models_to_dict_models(models: Iterable[Model]) -> list[DictModel]:
        pass

    @staticmethod
    def sql_model_to_dict_model(model: Model) -> DictModel:
        pass

    @staticmethod
    def redis_models_to_dict_models(models: Iterable[RedisModel]) -> list[DictModel]:
        pass

    @staticmethod
    def redis_model_to_dict_model(model: RoomRedis) -> DictModel:
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
    def hash_models_to_redis_models(models: Iterable[HashModel]) -> list[RedisModel]:
        pass

    @staticmethod
    def hash_model_to_redis_model(model_hash: DictModel) -> RoomRedis:
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
