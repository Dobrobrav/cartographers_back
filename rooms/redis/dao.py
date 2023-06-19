import json
from typing import Any, Optional, Iterable, Sequence

from django.contrib.auth.hashers import make_password
from djoser.conf import User

import services.utils
from cartographers_back.settings import REDIS
from services.redis.dao import UserDaoRedis
from services.redis.transformers import UserTransformer
from services.redis.transformers_base import DictModel
from services.redis.models_base import DataClassModel
from .dict_models import RoomDict, RoomPrettyForPage, RoomPretty
from .key_schemas import RoomKeySchema
from .transformers import RoomTransformer
from services.redis.redis_dao_base import DaoFull
from .dc_models import RoomDC


class RoomDaoRedis(DaoFull):
    _key_schema = RoomKeySchema()
    _transformer = RoomTransformer()
    _model_class = RoomDC

    def leave(self,
              user_id: int,
              ) -> None:
        room_id = self.get_room_id_by_user_id(user_id)
        self._delete_user(user_id, room_id)

    def _delete_user(self,
                     user_id: int,
                     room_id: int,
                     ) -> None:

        user_ids = self.get_model_attr(
            model_id=room_id,
            field_name='user_ids',
            converter=services.utils.deserialize,
        )
        user_ids.remove(user_id)

        self.set_model_attr(
            model_id=room_id,
            field_name='user_ids',
            value=user_ids,
            converter=services.utils.serialize,
        )

        self._delete_room_id_by_user_id_index(user_id)

    def _delete_room_id_by_user_id_index(self,
                                         user_id: int,
                                         ) -> None:
        key = self._key_schema.room_id_by_user_id_index_key
        self._redis.hdel(key, user_id)

    def check_user_is_admin(self,
                            user_id: int,
                            ) -> None:
        room_id = self.get_room_id_by_user_id(user_id)
        admin_id = self.fetch_dc_model(room_id=room_id).admin_id

        if user_id != admin_id:
            raise Exception('Game can only be started by its admin')

    def get_user_ids(self,
                     user_id: int,
                     ) -> list[int]:
        room_id = self.get_room_id_by_user_id(user_id)
        room = self.fetch_dc_model(room_id=room_id)
        player_ids = room.user_ids
        return player_ids

    def get_page(self,
                 page: int,
                 limit: int,
                 ) -> list[RoomPrettyForPage]:
        all_ids = self._get_all_ids()
        ids_for_page = self._get_ids_for_page(all_ids, page, limit)
        hash_rooms = self._fetch_hash_models(ids_for_page)
        rooms_dc: list[RoomDC] = self._transformer. \
            hash_models_to_dc_models(hash_rooms)

        page = self._transformer.make_pretty_rooms_for_page(rooms_dc)

        return page

    def delete_by_user_id(self,
                          user_id: int,
                          ) -> None:
        room_id = self.get_room_id_by_user_id(user_id)
        self.delete_by_id(room_id)

    def fetch_dc_model(self,
                       room_id: int | None = None,
                       room_name: str | None = None,
                       ) -> RoomDC:
        if room_id is not None:
            redis_model: RoomDC = super().fetch_dc_model(room_id)
        elif room_name is not None:
            redis_model: RoomDC = self._fetch_redis_model_by_name(room_name)
        else:
            raise ValueError()

        return redis_model

    def get_room_name(self,
                      room_id: int,
                      ) -> str:
        key = self._key_schema.get_hash_key(room_id)
        room_name = self._redis.hget(key, 'name')
        return room_name

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

        current_readiness = self._get_user_readiness(room_id, user_id)
        opposite_readiness = not current_readiness

        self._set_user_readiness(room_id, user_id, opposite_readiness)

        return opposite_readiness

    def get_room_id_by_user_id(self,
                               user_id: int,
                               ) -> int:
        key = self._key_schema.room_id_by_user_id_index_key
        room_id = int(self._redis.hget(key, user_id))
        print(room_id)

        return room_id

    def init_room(self,
                  name: str,
                  password: Optional[str],
                  max_users: int,
                  creator_id: int,
                  ) -> None:
        self._check_name_unique(name)

        room = self._create_dc_model(name, password, max_users, creator_id)
        self._set_user_readiness(room.id, creator_id, False)
        self._init_indexes(creator_id, room.id, name)
        self.insert_dc_model(room)

    def _create_dc_model(self,
                         name: str,
                         password: str,
                         max_users: int,
                         admin_id: int,
                         ) -> RoomDC:
        room = self._model_class(
            id=(room_id := self._gen_new_id()),
            name=name,
            password=make_password(password) if password else None,
            max_users=max_users,
            admin_id=admin_id,
            user_ids=[admin_id],
            is_game_started=False,
            # is_ready_for_game=False,
        )

        return room

    def _init_indexes(self,
                      creator_id: int,
                      room_id: int,
                      name: str,
                      ) -> None:

        self._add_room_id_by_user_id_index(
            user_id=creator_id, room_id=room_id
        )
        self._add_model_id_by_model_name_index(
            model_name=name, model_id=room_id
        )

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
        self._redis.hset(key, user_id, room_id)

    def kick_user(self,
                  kicker_id: int,
                  user_to_kick_id: int,
                  ) -> None:
        room_id = self._check_user_is_admin(kicker_id, user_to_kick_id)
        self._delete_user(user_to_kick_id, room_id)

    def _check_user_is_admin(self,
                             kicker_id: int,
                             kick_user_id: int,
                             ) -> int:
        room_id = self.get_room_id_by_user_id(kicker_id)
        ...
        return room_id

    # TODO: implement this

    def get_room_pretty(self,
                        user_id: Optional[int] = None,
                        room_id: Optional[int] = None,
                        ) -> dict[str, Any]:
        if room_id is not None:
            return self._get_room_pretty_by_room_id(room_id)
        elif user_id is not None:
            return self._get_room_pretty_by_user_id(user_id)
        else:
            raise ValueError()

    def _get_room_pretty_by_user_id(self,
                                    user_id: int,
                                    ) -> dict[str, Any]:
        room_id = self.get_room_id_by_user_id(user_id)
        room = self._get_room_pretty_by_room_id(room_id)
        return room

    def _get_room_pretty_by_room_id(self,
                                    room_id: int,
                                    ) -> RoomPretty:
        # костыли. надо прописать отдельный метод вроде make_room_pretty
        room_dc: RoomDC = self.fetch_dc_model(room_id=room_id)
        user_ids = room_dc.user_ids

        users_readiness = self._get_users_readiness(room_id, user_ids)
        users_pretty = UserDaoRedis(REDIS).get_users_pretty(user_ids,
                                                            users_readiness)

        room_dict = self._transformer.make_room_pretty(
            room_dc, self._check_room_ready_for_game(
                list(users_readiness.values())
            ),
            users_pretty
        )

        return room_dict

    def _check_room_ready_for_game(self,
                                   users_readiness: Sequence[bool],
                                   ) -> bool:
        return users_readiness.count(True) == len(users_readiness) - 1

    def _get_users_readiness(self,
                             room_id: int,
                             user_ids: Iterable[int],
                             ) -> dict[int, bool]:
        statuses = {
            user_id: self._get_user_readiness(room_id, user_id)
            for user_id in user_ids
        }
        return statuses

    def add_user(self,
                 room_id: int,
                 user_id: int,
                 ) -> None:
        # TODO: add NO more than max_users
        # add value to user_ids str -> fetch it change it set it
        user_ids = self.get_model_attr(
            model_id=room_id,
            field_name='user_ids',
            converter=services.utils.deserialize,
        )
        user_ids.append(user_id)

        self.set_model_attr(
            model_id=room_id,
            field_name='user_ids',
            value=user_ids,
            converter=services.utils.serialize,
        )
        self._add_room_id_by_user_id_index(user_id, room_id)
        self._set_user_readiness(room_id, user_id, readiness=False)

    def _set_user_readiness(self,
                            room_id: int,
                            user_id: int,
                            readiness: bool,
                            ) -> None:
        key = self._key_schema.user_readiness_key(room_id, user_id)
        self._redis.set(key, services.utils.serialize(readiness))

    def _get_user_readiness(self,
                            room_id: int,
                            user_id: int,
                            ) -> bool:
        key = self._key_schema.user_readiness_key(room_id, user_id)
        readiness = services.utils.deserialize(self._redis.get(key))
        return readiness
