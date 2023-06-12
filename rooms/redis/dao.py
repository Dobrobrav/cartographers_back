import json
from typing import Any, Optional

from django.contrib.auth.hashers import make_password
from djoser.conf import User

import services.utils
from cartographers_back.settings import REDIS
from services.redis.transformers import UserTransformer
from services.redis.transformers_base import DictModel
from services.redis.models_base import DataClassModel
from .dict_models import RoomDict, RoomDictForPage
from .key_schemas import RoomKeySchema
from .transformers import RoomTransformer
from services.redis.redis_dao_base import DaoFull
from .dc_models import RoomDC


class RoomDaoRedis(DaoFull):
    _key_schema = RoomKeySchema()
    _transformer = RoomTransformer()
    _model_class = RoomDC

    def leave_room(self,
                   user_id: int,
                   ) -> None:
        ...

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
                 ) -> list[RoomDictForPage]:
        all_ids = self._get_all_ids()
        ids_for_page = self._get_ids_for_page(all_ids, page, limit)
        hash_rooms = self._fetch_hash_models(ids_for_page)
        dict_rooms = self._transformer.hash_models_to_dict_models(hash_rooms)
        page = self._transformer.make_dict_rooms_for_page(dict_rooms)

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
        key = self._key_schema.get_user_readiness_key(user_id, room_id)
        current_state = bool(int(self._redis.get(key)))
        opposite_state = not current_state
        self._redis.set(key, int(opposite_state))

        return opposite_state

    def get_room_id_by_user_id(self,
                               user_id: int,
                               ) -> int:
        key = self._key_schema.room_id_by_user_id_index_key
        room_id = int(self._redis.hget(key, user_id))

        return room_id

    def create_room_dc(self,
                       name: str,
                       password: Optional[str],
                       max_users: int,
                       creator_id: int,
                       ) -> DataClassModel:
        print(password)
        room_id = self._gen_new_id()
        self._check_name_unique(name)
        model = self._model_class(
            id=room_id,
            name=name,
            password=make_password(password) if password else None,
            max_users=max_users,
            admin_id=creator_id,
            user_ids=[creator_id],
            is_game_started=False,
        )
        self._update_room_id_by_user_id_index(
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

    def _update_room_id_by_user_id_index(self,
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
        room_id = self._ckeck_user_is_admin(kicker_id, user_to_kick_id)

        user_ids = self.get_model_field(
            model_id=room_id,
            field_name='user_ids',
            converter=services.utils.load_seq,
        )
        user_ids.remove(user_to_kick_id)

        self.set_model_field(
            model_id=room_id,
            field_name='user_ids',
            value=user_ids,
            converter=services.utils.dump_seq,
        )

    def _ckeck_user_is_admin(self,
                             kicker_id: int,
                             kick_user_id: int,
                             ) -> int:
        room_id = self.get_room_id_by_user_id(kicker_id)
        ...
        return room_id

    # TODO: implement this

    def get_complete_room(self,
                          user_id: Optional[int] = None,
                          room_id: Optional[int] = None,
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
        room_dc: RoomDC = self.fetch_dc_model(room_id=room_id)
        user_ids = room_dc.user_ids

        sql_users = list(User.objects.filter(id__in=user_ids))
        dict_users = UserTransformer().sql_models_to_dict_models(sql_users)

        room_dict: RoomDict = self._transformer. \
            dc_model_to_dict_model(room_dc)
        room_dict['users'] = dict_users

        return room_dict

    def add_user(self,
                 room_id: int,
                 user_id: int,
                 ) -> None:
        # TODO: add NO more than max_users
        # add value to user_ids str -> fetch it change it set it
        user_ids = self.get_model_field(
            model_id=room_id,
            field_name='user_ids',
            converter=services.utils.load_seq,
        )
        user_ids.append(user_id)

        self.set_model_field(
            model_id=room_id,
            field_name='user_ids',
            value=user_ids,
            converter=services.utils.dump_seq,
        )
        self._update_room_id_by_user_id_index(user_id, room_id)
