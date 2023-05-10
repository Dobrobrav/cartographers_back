from django.contrib.auth.hashers import make_password

from services.redis_models_base import RedisModel
from .key_schemas import RoomKeySchema
from .model_transformers import RoomTransformer
from services.redis_dao_base import DaoRedis
from .models import RoomRedis


class RoomDaoRedis(DaoRedis):
    _key_schema = RoomKeySchema()
    _transformer = RoomTransformer()
    _model = RoomRedis

    def create_room(self,
                    name: str,
                    password: str,
                    max_players: int,
                    token: str,
                    ) -> RedisModel:
        id = self._gen_new_id()
        # admin_id = _get_admin_id_by_token(token)  # user_id по токену достать просто,
        admin_id = 5
        model = self._model(
            id=id,
            name=name,
            password=make_password(password),
            max_players=max_players,
            admin_id=admin_id,
        )
        return model
