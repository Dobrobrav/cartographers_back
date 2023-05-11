from django.contrib.auth.hashers import make_password

from services.redis.redis_models_base import RedisModel
from .key_schemas import RoomKeySchema
from .model_transformers import RoomTransformer
from services.redis.redis_dao_base import DaoRedis
from .models import RoomRedis


class RoomDaoRedis(DaoRedis):
    _key_schema = RoomKeySchema()
    _transformer = RoomTransformer()
    _model = RoomRedis

    def create_room(self,
                    name: str,
                    password: str,
                    max_players: int,
                    creator_id: int,
                    ) -> RedisModel:
        id = self._gen_new_id()
        model = self._model(
            id=id,
            name=name,
            password=make_password(password),
            max_players=max_players,
            admin_id=creator_id,
            users=[creator_id],
        )
        return model

    def add_user(self,
                 user_id: int,
                 ) -> None:
        pass

