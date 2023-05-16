from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from services.redis.redis_models_base import RedisModel
from .key_schemas import RoomKeySchema
from .model_transformers import RoomTransformer
from services.redis.redis_dao_base import DaoRedisRedis, DaoRedisSQL
from .models import RoomRedis


class RoomDaoRedis(DaoRedisRedis):
    _key_schema = RoomKeySchema()
    _transformer = RoomTransformer()
    _model_class = RoomRedis

    def create_room(self,
                    name: str,
                    password: str,
                    max_users: int,
                    creator_id: int,
                    ) -> RedisModel:
        id = self._gen_new_id()
        model = self._model_class(
            id=id,
            name=name,
            password=make_password(password),
            max_users=max_users,
            admin_id=creator_id,
            user_ids=[creator_id],
        )
        return model

    def get_room_with_actual_users(self,
                                   room_id: int,
                                   ) -> dict[str, Any]:
        room: RoomRedis = self.fetch_model(model_id=room_id)
        user_ids = room.user_ids
        users = list(get_user_model().objects.filter(id__in=user_ids))
        room_dict = self._transformer.redis_model_to_dict(room)
        # user_dao = UserDaoRedis(self._redis)
        room_dict['users'] = users

        return room_dict

    def add_user(self,
                 room_id: int,
                 user_id: int,
                 ) -> None:
        # TODO: add no more than max_users
        room = self.fetch_model(room_id)
        room.user_ids.append(user_id)
        self.insert_redis_model(room)
