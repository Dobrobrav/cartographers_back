from typing import Iterable, MutableSequence
from services import utils
from rooms.redis.dc_models import RoomDC
from rooms.redis.dict_models import RoomDict, RoomPrettyForPage, RoomPretty
from rooms.redis.hash_models import RoomHash
from services.redis.dict_models import UserPretty
from services.redis.base.converters_base import BaseRedisConverter


class RoomConverter(BaseRedisConverter):

    @staticmethod
    def dc_model_to_dict_model(dc_model: RoomDC,
                               ) -> RoomDict:
        room_dict = RoomDict(
            id=dc_model.id,
            name=dc_model.name,
            password=dc_model.password or '',
            max_users=dc_model.max_users,
            admin_id=dc_model.admin_id,
            user_ids=utils.serialize(dc_model.user_ids),
            is_game_started=utils.serialize(
                dc_model.is_game_started
            ),
            # is_ready_for_game=services.utils.serialize(
            #     dc_model.is_ready_for_game
            # ),
        )
        return room_dict

    @staticmethod
    def make_room_pretty(dc_model: RoomDC,
                         is_ready_for_game: bool,
                         users_pretty: MutableSequence[UserPretty]
                         ) -> RoomPretty:
        room = RoomPretty(
            id=dc_model.id,
            name=dc_model.name,
            password=dc_model.password,
            max_users=dc_model.max_users,
            admin_id=dc_model.admin_id,
            user_ids=dc_model.user_ids,
            users=users_pretty,
            is_game_started=dc_model.is_game_started,
            is_ready_for_game=is_ready_for_game,
        )
        return room

    @staticmethod
    def hash_model_to_dc_model(hash_model: RoomHash,
                               ) -> RoomDC:
        redis_model = RoomDC(
            id=int(hash_model[b'id']),
            name=hash_model[b'name'].decode('utf-8'),
            password=hash_model[b'password'].decode('utf-8') or None,
            max_users=int(hash_model[b'max_users']),
            admin_id=int(hash_model[b'admin_id']),
            user_ids=utils.deserialize(hash_model[b'user_ids']),
            is_game_started=utils.deserialize(
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
