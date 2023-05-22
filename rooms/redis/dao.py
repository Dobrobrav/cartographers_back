from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from cartographers_back.settings import REDIS
from services.redis.dao import UserDaoRedis
from services.redis.model_transformers import UserTransformer
from services.redis.model_transformers_base import DictModel
from services.redis.redis_models_base import RedisModel
from .key_schemas import RoomKeySchema
from .model_transformers import RoomTransformer
from services.redis.redis_dao_base import DaoRedisRedis, DaoRedisSQL
from .models import RoomRedis


class RoomDaoRedis(DaoRedisRedis):
    _key_schema = RoomKeySchema()
    _transformer = RoomTransformer()
    _model_class = RoomRedis

    def leave_room(self,
                   user_id: int,
                   ) -> None:
        ...

    def get_page(self,
                 page: int,
                 limit: int,
                 ) -> list[RedisModel]:
        all_ids = self._get_all_ids()
        ids_for_page = self._get_ids_for_page(all_ids, page, limit)
        hash_models = self.fetch_hash_models(ids_for_page)
        redis_models = self._transformer. \
            hash_models_to_redis_models(hash_models)

        return redis_models

    def delete_by_user_id(self,
                          user_id: int,
                          ) -> None:
        room_id = self.get_room_id_by_user_id(user_id)
        self.delete_by_id(room_id)

    def change_user_readiness(self,
                              user_id: int,
                              ) -> bool:
        room_id = self.get_room_id_by_user_id(user_id)
        key = self._key_schema.get_user_readiness_key(user_id, room_id)
        current_state = bool(int(self._redis.get(key)))
        opposite_state = not current_state
        self._redis.set(key, int(opposite_state))

        return opposite_state

    def get_room_id_by_user_id(self,
                               user_id: int,
                               ) -> int:
        key = self._key_schema.get_user_id_room_id_index_key()
        room_id = int(self._redis.zscore(key, user_id))

        return room_id

    def create_room(self,
                    name: str,
                    password: str,
                    max_users: int,
                    creator_id: int,
                    ) -> RedisModel:
        room_id = self._gen_new_id()
        model = self._model_class(
            id=room_id,
            name=name,
            password=make_password(password),
            max_users=max_users,
            admin_id=creator_id,
            user_ids=[creator_id],
        )
        self._update_user_id_room_id_index(
            user_id=creator_id, room_id=room_id
        )
        return model

    def _update_user_id_room_id_index(self,
                                      user_id: int,
                                      room_id: int,
                                      ) -> None:
        """ score - user_id; member - room_id. room_ids are sorted by user_ids """
        key = self._key_schema.get_user_id_room_id_index_key()
        self._redis.zadd(key, {user_id: room_id})

    def kick_user(self,
                  admin_id: int,
                  kick_user_id: int,
                  ) -> DictModel:
        ...

    # TODO: implement this

    def get_complete_room(self,
                          user_id: int | None = None,
                          room_id: int | None = None,
                          ) -> dict[str, Any]:
        if room_id is not None:
            self._get_complete_room_by_room_id(room_id)
        elif user_id is not None:
            self._get_complete_room_by_user_id(user_id)
        else:
            raise ValueError()

    def _get_complete_room_by_user_id(self,
                                      user_id: int,
                                      ) -> dict[str, Any]:
        room_id = self.get_room_id_by_user_id(user_id)
        room = self._get_complete_room_by_room_id(room_id)
        return room

    def _get_complete_room_by_room_id(self,
                                      room_id: int,
                                      ) -> dict[str, Any]:
        room: RoomRedis = self.fetch_redis_model(model_id=room_id)
        user_ids = room.user_ids

        sql_users = list(get_user_model().objects.filter(id__in=user_ids))
        dict_users = UserTransformer.sql_models_to_dict_models(sql_users)

        dict_room = self._transformer.redis_model_to_dict_model(room)
        dict_room['users'] = dict_users

        return dict_room

    def add_user(self,
                 room_id: int,
                 user_id: int,
                 ) -> None:
        # TODO: add NO more than max_users
        room = self.fetch_redis_model(room_id)
        room.user_ids.append(user_id)
        self.insert_redis_model(room)
