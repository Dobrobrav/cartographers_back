from typing import Any, Optional, Iterable, Sequence

from django.contrib.auth.hashers import make_password

import services.utils
from cartographers_back.settings import REDIS
from services.redis.dao import UserDaoRedis
from services.redis.base.models_base import DataClassModel
from .dict_models import RoomPrettyForPage, RoomPretty
from .key_schemas import RoomKeySchema
from .converters import RoomConverter
from services.redis.base.redis_dao_base import DaoFull
from .dc_models import RoomDC
from ..common import UserNotInRoom


class RoomDaoRedis(DaoFull):
    _key_schema = RoomKeySchema()
    _converter = RoomConverter()
    _model_class = RoomDC

    def try_init_room(self,
                      name: str,
                      password: Optional[str],
                      max_users: int,
                      creator_id: int,
                      ) -> None:
        self._check_name_unique(name)
        self._init_room(name, password, max_users, creator_id)

    def _init_room(self,
                   name: str,
                   password: str,
                   max_users: int,
                   creator_id: int,
                   ) -> None:
        room = self._create_dc_model(name, password, max_users, creator_id)
        self._set_user_is_ready(room.id, creator_id, False)
        self._init_indexes(creator_id, room.id, name)
        self.insert_dc_model(room)

    def fetch_room_pretty(self,
                          user_id: Optional[int] = None,
                          room_id: Optional[int] = None,
                          ) -> dict[str, Any]:
        if room_id is not None:
            return self._fetch_room_pretty_by_room_id(room_id)
        elif user_id is not None:
            return self._fetch_room_pretty_by_user_id(user_id)
        else:
            raise ValueError()

    def try_kick_user(self,
                      kicker_id: int,
                      user_to_kick_id: int,
                      ) -> None:
        room_id = self._fetch_room_id_by_user_id(user_to_kick_id)
        self.check_user_is_admin(room_id, kicker_id)
        self._delete_user(user_to_kick_id, room_id)

    def try_leave(self,
                  user_id: int,
                  ) -> None:
        room_id = self._fetch_room_id_by_user_id(user_id)
        self._delete_user(user_id, room_id)

    def set_is_game_started(self,
                            room_id: int,
                            is_game_started: bool,
                            ) -> None:
        self._set_model_attr(
            room_id, 'is_game_started',
            is_game_started, services.utils.serialize,
        )

    def check_user_is_admin(self,
                            room_id: int,
                            user_id: int,
                            ) -> None:
        admin_id = self._fetch_admin_id(room_id)

        if user_id != admin_id:
            raise Exception('Game can only be started by its admin')

    def fetch_user_ids(self,
                       user_id: int,
                       ) -> list[int]:
        room_id = self._fetch_room_id_by_user_id(user_id)
        room = self.fetch_dc_model(room_id=room_id)
        player_ids = room.user_ids
        return player_ids

    def fetch_page(self,
                   page: int,
                   limit: int,
                   ) -> list[RoomPrettyForPage]:
        all_ids = self._get_all_ids()
        ids_for_page = self._get_ids_for_page(all_ids, page, limit)
        hash_rooms = self._fetch_hash_models(ids_for_page)
        rooms_dc: list[RoomDC] = self._Converter. \
            hash_models_to_dc_models(hash_rooms)

        page = self._Converter.make_pretty_rooms_for_page(rooms_dc)

        return page

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

    def fetch_room_name(self,
                        room_id: int,
                        ) -> str:
        room_name = self._fetch_model_attr(
            model_id=room_id,
            field_name='name',
            converter=services.utils.decode_bytes,
        )
        return room_name

    def add_user(self,
                 room_id: int,
                 user_id: int,
                 ) -> None:
        self._check_users_quantity(room_id)
        self._add_user_id(room_id, user_id)
        self._set_user_is_ready(room_id, user_id, is_ready=False)
        self._add_room_id_by_user_id_index(user_id, room_id)

    def change_user_is_ready(self,
                             user_id: int,
                             ) -> None:
        room_id = self._fetch_room_id_by_user_id(user_id)

        current_readiness = self._fetch_user_is_ready(room_id, user_id)
        self._set_user_is_ready(room_id, user_id, not current_readiness)

    def _fetch_room_id_by_user_id(self,
                                  user_id: int,
                                  ) -> int:
        key = self._key_schema.room_id_by_user_id_index_key
        room_id = self.fetch_hash_value(key, user_id, converter=int)
        if room_id is None:
            raise UserNotInRoom()
        return room_id

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

    def _fetch_admin_id(self,
                        room_id: int,
                        ) -> int:
        admin_id = self._fetch_model_attr(
            room_id, 'admin_id', services.utils.deserialize
        )
        return admin_id

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

    def _delete_room_id_by_user_id_index(self,
                                         user_id: int,
                                         ) -> None:
        key = self._key_schema.room_id_by_user_id_index_key
        self._redis.hdel(key, user_id)

    def _add_model_id_by_model_name_index(self,
                                          model_name: str,
                                          model_id: int,
                                          ) -> None:
        key = self._key_schema.model_id_by_model_name_index_key
        self._redis.hset(key, model_name, model_id)

    def _check_users_quantity(self,
                              room_id: int,
                              ) -> None:
        ...

    def _add_user_id(self,
                     room_id: int,
                     user_id: int,
                     ) -> None:
        user_ids = self._fetch_user_ids(room_id)
        user_ids.append(user_id)

        self._set_model_attr(
            model_id=room_id,
            field_name='user_ids',
            value=user_ids,
            converter=services.utils.serialize,
        )

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

    def _delete_user(self,
                     user_id: int,
                     room_id: int,
                     ) -> None:
        self._remove_user_id(room_id, user_id)
        self._delete_room_id_by_user_id_index(user_id)

    def _remove_user_id(self,
                        room_id: int,
                        user_id: int,
                        ) -> None:
        user_ids = self._fetch_user_ids(room_id)
        user_ids.remove(user_id)
        self._set_user_ids(room_id, user_ids)

    def _fetch_user_ids(self,
                        room_id: int,
                        ) -> list[int]:
        user_ids = self._fetch_model_attr(
            model_id=room_id,
            field_name='user_ids',
            converter=services.utils.deserialize,
        )
        return user_ids

    def _set_user_ids(self,
                      room_id: int,
                      user_ids: Sequence[int],
                      ) -> None:
        self._set_model_attr(
            model_id=room_id,
            field_name='user_ids',
            value=user_ids,
            converter=services.utils.serialize,
        )

    def _fetch_room_pretty_by_user_id(self,
                                      user_id: int,
                                      ) -> dict[str, Any]:
        room_id = self._fetch_room_id_by_user_id(user_id)
        room = self._fetch_room_pretty_by_room_id(room_id)
        return room

    def _fetch_redis_model_by_name(self,
                                   model_name: str,
                                   ) -> DataClassModel:
        model_id = self._get_id_by_name(model_name)
        redis_model = super().fetch_dc_model(model_id)
        return redis_model

    def _fetch_room_pretty_by_room_id(self,
                                      room_id: int,
                                      ) -> RoomPretty:
        room_dc: RoomDC = self.fetch_dc_model(room_id=room_id)
        user_ids = room_dc.user_ids

        users_readiness = self._fetch_user_is_ready_many(room_id, user_ids)
        users_pretty = UserDaoRedis(REDIS).get_users_pretty(user_ids,
                                                            users_readiness)

        room_dict = self._Converter.make_room_pretty(
            room_dc, self._check_room_is_ready_for_game(
                list(users_readiness.values())
            ),
            users_pretty
        )

        return room_dict

    def _check_room_is_ready_for_game(self,
                                      users_readiness: Sequence[bool],
                                      ) -> bool:
        return users_readiness.count(True) == len(users_readiness) - 1

    def _fetch_user_is_ready_many(self,
                                  room_id: int,
                                  user_ids: Iterable[int],
                                  ) -> dict[int, bool]:
        statuses = {
            user_id: self._fetch_user_is_ready(room_id, user_id)
            for user_id in user_ids
        }
        return statuses

    def _set_user_is_ready(self,
                           room_id: int,
                           user_id: int,
                           is_ready: bool,
                           ) -> None:
        key = self._key_schema.user_readiness_key(room_id, user_id)
        self._redis.set(key, services.utils.serialize(is_ready))

    def _fetch_user_is_ready(self,
                             room_id: int,
                             user_id: int,
                             ) -> bool:
        key = self._key_schema.user_readiness_key(room_id, user_id)
        readiness = services.utils.deserialize(self._redis.get(key))
        return readiness

    def _get_id_by_name(self,
                        model_name: str,
                        ) -> int:
        key = self._key_schema.model_id_by_model_name_index_key
        model_id = int(self._redis.hget(key, model_name))
        return model_id
