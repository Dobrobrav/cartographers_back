import json
from typing import Iterable

from rooms.redis.dc_models import RoomDC
from rooms.redis.dict_models import RoomDict, RoomDictForPage
from rooms.redis.hash_models import RoomHash
from services.redis.transformers_base import BaseRedisTransformer
from services.utils import decode_bytes


class RoomTransformer(BaseRedisTransformer):

    @staticmethod
    def dc_model_to_dict_model(dc_model: RoomDC,
                               ) -> RoomDict:
        room_dict = RoomDict(
            id=dc_model.id,
            name=dc_model.name,
            password=dc_model.password or '',
            max_users=dc_model.max_users,
            admin_id=dc_model.admin_id,
            user_ids=json.dumps(dc_model.user_ids),
            is_game_started=int(dc_model.is_game_started),
        )
        return room_dict

    @staticmethod
    def hash_model_to_dc_model(hash_model: RoomHash,
                               ) -> RoomDC:
        redis_model = RoomDC(
            id=int(hash_model[b'id']),
            name=hash_model[b'name'].decode('utf-8'),
            password=hash_model[b'password'].decode('utf-8') or None,
            max_users=int(hash_model[b'max_users']),
            admin_id=int(hash_model[b'admin_id']),
            user_ids=json.loads(decode_bytes(hash_model[b'user_ids'])),
            is_game_started=bool(int(hash_model[b'is_game_started'])),
        )

        return redis_model

    def make_dict_rooms_for_page(self,
                                 dict_models: Iterable[RoomDict],
                                 ) -> list[RoomDictForPage]:
        """ rooms in dict-format for page of rooms """
        display_dict_rooms = [
            self.make_dict_room_for_page(room_dict)
            for room_dict in dict_models
        ]
        return display_dict_rooms

    @staticmethod
    def make_dict_room_for_page(dict_room: RoomDict,
                                ) -> RoomDictForPage:
        room = RoomDictForPage(
            id=dict_room['id'],
            name=dict_room['name'],
            max_users=dict_room['max_users'],
            current_users=len(dict_room['user_ids'].split()),
            contains_password=bool(dict_room['password']),
            is_game_started=bool(dict_room['is_game_started']),
        )
        return room
