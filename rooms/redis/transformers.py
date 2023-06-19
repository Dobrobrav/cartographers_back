import json
from typing import Iterable

import services.utils
from rooms.redis.dc_models import RoomDC
from rooms.redis.dict_models import RoomDict, RoomPrettyForPage
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
            is_game_started=services.utils.serialize(
                dc_model.is_game_started
            ),
            # is_ready_for_game=services.utils.serialize(
            #     dc_model.is_ready_for_game
            # ),
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
            user_ids=services.utils.deserialize(hash_model[b'user_ids']),
            is_game_started=services.utils.deserialize(
                hash_model[b'is_game_started']
            ),
            # is_ready_for_game=services.utils.deserialize(
            #     hash_model[b'is_ready_for_game']
            # )
        )

        return redis_model

    def make_pretty_rooms_for_page(self,
                                   dc_models: Iterable[RoomDC],
                                   ) -> list[RoomPrettyForPage]:
        """ rooms in dict-format for page of rooms """
        rooms_pretty = [
            self.make_pretty_room_for_page(room_dc)
            for room_dc in dc_models
        ]
        return rooms_pretty

    @staticmethod
    def make_pretty_room_for_page(room_dc: RoomDC,
                                  ) -> RoomPrettyForPage:
        room_pretty = RoomPrettyForPage(
            id=room_dc.id,
            name=room_dc.name,
            max_users=room_dc.max_users,
            current_users=len(room_dc.user_ids),
            contains_password=bool(room_dc.password),
            is_game_started=room_dc.is_game_started,
            # is_ready_for_game=room_dc.is_ready_for_game,
        )
        return room_pretty
