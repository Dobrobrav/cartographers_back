from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from services.redis.model_transformers import UserTransformer
from services.redis.model_transformers_base import DictModel
from services.redis.redis_models_base import DataClassModel
from .key_schemas import RoomKeySchema
from .model_transformers import RoomTransformer
from services.redis.redis_dao_base import DaoRedis, DaoSQL
from .models import RoomDC


class RoomDaoRedis(DaoRedis):
    _key_schema = RoomKeySchema()
    _transformer = RoomTransformer()
    _model_class = RoomDC

    def leave_room(self,
                   user_id: int,
                   ) -> None:
        ...

    def get_player_ids(self,
                       user_id: int,
                       ) -> list[int]:
        room_id = self.get_room_id_by_user_id(user_id)
        room = self.fetch_dc_model(room_id=room_id)
        player_ids = room.user_ids
        return player_ids

    def get_page(self,
                 page: int,
                 limit: int,
                 ) -> list[DataClassModel]:
        all_ids = self._get_all_ids()
        ids_for_page = self._get_ids_for_page(all_ids, page, limit)
        hash_models = self._fetch_hash_models(ids_for_page)
        redis_models = self._transformer. \
            hash_models_to_dc_models(hash_models)

        return redis_models

    def delete_by_user_id(self,
                          user_id: int,
                          ) -> None:
        room_id = self.get_room_id_by_user_id(user_id)
        self.delete_by_id(room_id)

    def fetch_dc_model(self,
                       room_id: int | None = None,
                       room_name: str | None = None,
                       ) -> DataClassModel:
        if room_id is not None:
            redis_model = super().fetch_dc_model(room_id)
        elif room_name is not None:
            redis_model = self._fetch_redis_model_by_name(room_name)
        else:
            raise ValueError()

        return redis_model

    def _fetch_redis_model_by_name(self,
                                   model_name: str,
                                   ) -> DataClassModel:
        model_id = self._get_id_by_name(model_name)
        redis_model = super().fetch_dc_model(model_id)
        return redis_model

    def _get_id_by_name(self,
                        model_name: str,
                        ) -> int:
        key = self._key_schema.model_id_by_model_name_index_key
        model_id = int(self._redis.hget(key, model_name))
        return model_id

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
        key = self._key_schema.room_id_by_user_id_index_key
        room_id = int(self._redis.zscore(key, user_id))

        return room_id

    def create_room(self,
                    name: str,
                    password: str,
                    max_users: int,
                    creator_id: int,
                    ) -> DataClassModel:
        room_id = self._gen_new_id()
        self._check_name_unique(name)
        model = self._model_class(
            id=room_id,
            name=name,
            password=make_password(password),
            max_users=max_users,
            admin_id=creator_id,
            user_ids=[creator_id],
        )
        self._add_room_id_by_user_id_index(
            user_id=creator_id, room_id=room_id
        )
        self._add_model_id_by_model_name_index(
            model_name=name, model_id=room_id
        )
        return model

    def _add_model_id_by_model_name_index(self,
                                          model_name: str,
                                          model_id: int,
                                          ) -> None:
        key = self._key_schema.model_id_by_model_name_index_key
        self._redis.hset(key, model_name, model_id)

    def _check_name_unique(self,
                           name: str,
                           ) -> None:
        pass

    def _add_room_id_by_user_id_index(self,
                                      user_id: int,
                                      room_id: int,
                                      ) -> None:
        """ score - user_id; member - room_id. room_ids are sorted by user_ids """
        key = self._key_schema.room_id_by_user_id_index_key
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
            return self._get_complete_room_by_room_id(room_id)
        elif user_id is not None:
            return self._get_complete_room_by_user_id(user_id)
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
        redis_room: RoomDC = self.fetch_dc_model(room_id=room_id)
        user_ids = redis_room.user_ids

        sql_users = list(get_user_model().objects.filter(id__in=user_ids))
        dict_users = UserTransformer().sql_models_to_dict_models(sql_users)

        dict_room = self._transformer.dc_model_to_dict_model(redis_room)
        dict_room['users'] = dict_users

        return dict_room

    def add_user(self,
                 room_id: int,
                 user_id: int,
                 ) -> None:
        # TODO: add NO more than max_users
        room = self.fetch_dc_model(room_id)
        room.user_ids.append(user_id)
        self.insert_dc_model(room)
