from django.db.models import Model

from rooms.redis.models import RoomRedis
from services.redis.model_transformers_base import ITransformer, ModelHash


class RoomTransformer(ITransformer):
    @staticmethod
    def dump_sql_model(model: Model) -> ModelHash:
        pass

    @staticmethod
    def dump_redis_model(model: RoomRedis) -> ModelHash:
        hash = {
            'id': model.id,
            'name': model.name,
            'password': model.password,
            'max_players': model.max_players,
            'admin_id': model.admin_id,
            'user_ids': ' '.join(
                str(user_id)
                for user_id in model.user_ids
            ),
        }
        return hash

    @staticmethod
    def load_redis_model(model_hash: ModelHash) -> RoomRedis:
        room = RoomRedis(
            id=int(model_hash['id']),
            name=model_hash['name'],
            password=model_hash['password'],
            max_players=int(model_hash['max_players']),
            admin_id=int(model_hash['admin_id']),
            user_ids=[
                int(user_id)
                for user_id in model_hash['user_ids'].split()
            ],
        )
        return room
