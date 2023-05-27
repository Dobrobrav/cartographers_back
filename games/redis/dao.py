import random
from typing import Iterable

from cartographers_back.settings import REDIS
from rooms.redis.dao import RoomDaoRedis
from services.redis.model_transformers_base import DictModel
from services.redis.redis_dao_base import DaoRedisRedis, DaoRedisSQL
from .key_schemas import MonsterCardKeySchema, GameKeySchema, SeasonKeySchema, MoveKeySchema, PlayerKeySchema, \
    DiscoveryCardKeySchema
from .model_transformers import MonsterCardTransformer, GameTransformer, SeasonTransformer, MoveTransformer, \
    PlayerTransformer, DiscoveryCardTransformer
from .models import SeasonRedis, GameRedis


class GameDaoRedis(DaoRedisRedis):
    MONSTER_CARDS_AMOUNT = 4

    _key_schema = GameKeySchema()
    _transformer = GameTransformer()

    # TODO: keep in mind that DictModel is for redis, not necessarily for Response
    # TODO: can I create a base typed dict class for models and inherit from it?
    # TODO: point of redis models is that I operate with them and  transform it into other forms to send it somewhere
    def start_game(self,
                   admin_id: int,
                   ) -> DictModel:
        discovery_card_ids_pull = DiscoveryCardDaoRedis(REDIS). \
            pick_discovery_cards()
        monster_card_ids_pull = MonsterCardDaoRedis(REDIS). \
            pick_monster_cards()
        season_card_ids_pull = self._prepare_season_cards()

        room_dao = RoomDaoRedis(REDIS)
        player_ids = room_dao.get_player_ids(admin_id)
        lobby_id = room_dao.get_room_id_by_user_id(admin_id)

        first_move_id = self.start_new_move()

        game = self._build_game_model(
            discovery_card_ids_pull,
            monster_card_ids_pull,
            season_card_ids_pull,
            player_ids,
            lobby_id,
            admin_id
        )
        dict_game = self.insert_redis_model(game)

        return dict_game

    def start_new_move(self,
                       game_id):
        ...

    def _build_game_model(self,
                          discovery_cards: Iterable[int],
                          monster_cards: Iterable[int],
                          season_cards: Iterable[int],
                          players: Iterable[int],
                          lobby_id: int,
                          admin_id: int,
                          ) -> GameRedis:
        game = GameRedis(
            id=self._gen_new_id(),
            lobby_id=lobby_id,
            monster_card_for_game_ids=monster_cards,
            season_for_game_ids=season_cards,
            discovery_card_for_game_ids=discovery_cards,
            player_ids=players,
            admin_id=admin_id,
        )

    def _prepare_season_cards(self,
                              ) -> list[int]:
        """ create season_cards, insert them into redis
         and return their ids """
        ...


class DiscoveryCardDaoRedis(DaoRedisRedis, DaoRedisSQL):
    DISCOVERY_CARD_QUANTITY = 20

    _key_schema = DiscoveryCardKeySchema()
    _transformer = DiscoveryCardTransformer()

    def pick_discovery_cards(self):  # TODO: move this method into DiscoveryCardDaoRedis!
        card_ids_key = self._key_schema.ids_key
        card_ids = self._redis.smembers(card_ids_key)

        picked_card_ids = random.sample(card_ids,
                                        self.DISCOVERY_CARD_QUANTITY)
        return picked_card_ids


class SeasonDaoRedis(DaoRedisRedis):
    _key_schema = SeasonKeySchema()
    _transformer = SeasonTransformer()


class MoveDaoRedis(DaoRedisRedis):
    _key_schema = MoveKeySchema()
    _transformer = MoveTransformer()


class PlayerDaoRedis(DaoRedisRedis):
    _key_schema = PlayerKeySchema()
    _transformer = PlayerTransformer()


class MonsterCardDaoRedis(DaoRedisRedis, DaoRedisSQL):
    _key_schema = MonsterCardKeySchema()
    _transformer = MonsterCardTransformer()

    def pick_monster_cards(self,
                           ) -> list[int]:
        pass
