from django.contrib.auth.hashers import make_password

from services.redis.redis_models_base import RedisModel
from .key_schemas import RoomKeySchema
from .model_transformers import RoomTransformer
from services.redis.redis_dao_base import DaoRedisRedis, DaoRedisSQL
from .models import RoomRedis


class RoomDaoRedis(DaoRedisRedis):
    _key_schema = RoomKeySchema()
    _transformer = RoomTransformer()
    _model = RoomRedis

    def create_room(self,
                    name: str,
                    password: str,
                    max_users: int,
                    creator_id: int,
                    ) -> RedisModel:
        id = self._gen_new_id()
        model = self._model(
            id=id,
            name=name,
            password=make_password(password),
            max_users=max_users,
            admin_id=creator_id,
            user_ids=[creator_id],
        )
        return model

    def add_user(self,
                 room_id: int,
                 user_id: int,
                 ) -> None:
        # TODO: add no more than max_users
        room = self.fetch_model(room_id)
        room.user_ids.append(user_id)
        self.insert_redis_model(room)
