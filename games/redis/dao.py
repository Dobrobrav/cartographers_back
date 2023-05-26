from typing import Iterable

from cartographers_back.settings import REDIS
from rooms.redis.dao import RoomDaoRedis
from services.redis.model_transformers_base import DictModel
from services.redis.redis_dao_base import DaoRedisRedis, DaoRedisSQL
from .key_schemas import MonsterCardKeySchema, GameKeySchema, SeasonKeySchema, MoveKeySchema, PlayerKeySchema
from .model_transformers import MonsterCardTransformer, GameTransformer, SeasonTransformer, MoveTransformer, \
    PlayerTransformer
from .models import SeasonRedis, GameRedis


class GameDaoRedis(DaoRedisRedis):
    _key_schema = GameKeySchema()
    _transformer = GameTransformer()

    # TODO: keep in mind that DictModel is for redis, not necessarily for Response
    # TODO: can I create a base typed dict class for models and inherit from it?
    # TODO: point of redis models is that I operate with them and  transform it into other forms to send it somewhere
    def start_game(self,
                   admin_id: int,
                   ) -> DictModel:
        discovery_card_ids_pull = self._pick_discovery_cards()
        monster_card_ids_pull = self._pick_monster_cards()
        season_card_ids_pull = self._prepare_season_cards()
        players = self._collect_players(admin_id)
        lobby_id = RoomDaoRedis(REDIS).get_room_id_by_user_id(admin_id)

        game = self._build_game_model(
            discovery_card_ids_pull,
            monster_card_ids_pull,
            season_card_ids_pull,
            players,
            lobby_id,
        )
        dict_game = self.insert_redis_model(game)

        return dict_game

    def _build_game_model(self,
                          discovery_cards: Iterable[int],
                          monster_cards: Iterable[int],
                          season_cards: Iterable[int],
                          players: Iterable[int],
                          lobby_id: int,
                          ) -> GameRedis:
        pass

    def _prepare_season_cards(self,
                              ) -> list[int]:
        """ create season_cards, insert them into redis
         and return their ids """
        objective_card_ids_pull = self._pick_objective_cards()
        pass


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
