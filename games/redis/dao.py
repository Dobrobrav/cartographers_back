import random
from dataclasses import dataclass
from typing import Iterable

from cartographers_back.settings import REDIS
from rooms.redis.dao import RoomDaoRedis
from services.redis.model_transformers_base import DictModel
from services.redis.redis_dao_base import DaoRedisRedis, DaoRedisSQL
from .key_schemas import MonsterCardKeySchema, GameKeySchema, SeasonKeySchema, MoveKeySchema, PlayerKeySchema, \
    TerrainCardKeySchema, ObjectiveCardKeySchema
from .model_transformers import MonsterCardTransformer, GameTransformer, SeasonTransformer, MoveTransformer, \
    PlayerTransformer, TerrainCardTransformer, ObjectiveCardTransformer
from .models import SeasonRedis, GameRedis, MoveRedis, TerrainCardRedis
from enum import Enum


class EDiscoveryCardType(Enum):
    TERRAIN = 'terrain'
    MONSTER = 'monster'


class ESeasonName(Enum):
    SPRING = 'spring'
    SUMMER = 'summer'
    FALL = 'fall'
    WINTER = 'winter'


class GameDaoRedis(DaoRedisRedis):
    MONSTER_CARDS_AMOUNT = 4
    SEASONS_IN_GAME = 4

    _key_schema = GameKeySchema()
    _transformer = GameTransformer()

    # TODO: keep in mind that DictModel is for redis, not necessarily for Response
    # TODO: can I create a base typed dict class for models and inherit from it?
    # TODO: point of redis models is that I operate with them and  transform it into other forms to send it somewhere
    def start_game(self,
                   admin_id: int,
                   ) -> DictModel:
        # каждый сезон карты местности перетасовываются, а после хода карта откладывается
        # I think moves should be in season's responsibility

        terrain_card_ids_pull = TerrainCardDaoRedis(REDIS). \
            pick_terrain_cards()

        monster_card_ids_pull = MonsterCardDaoRedis(REDIS). \
            pick_monster_cards()

        season_ids_pull = self.init_seasons()

        room_dao = RoomDaoRedis(REDIS)
        player_ids = room_dao.get_player_ids(admin_id)
        room_id = room_dao.get_room_id_by_user_id(admin_id)

        game = self._create_game_model(
            terrain_cards=terrain_card_ids_pull,
            monster_cards=monster_card_ids_pull,
            season_ids=season_ids_pull,
            players=player_ids,
            room_id=room_id,
            admin_id=admin_id,
        )
        season_id = self._start_first_season(game)

        first_move = self.start_first_move(
            season_ids_pull,
            terrain_card_ids_pull,
            monster_card_ids_pull,
        )

        dict_game = self.insert_redis_model(game)

        return dict_game

    def start_first_season(self,
                           game: GameRedis,
                           ) -> SeasonRedis:
        id = self._gen_new_id()
        season_points =

    def start_new_move(self,
                       game_id: int,
                       ) -> int:
        if game_id is None:
            ...

    def start_first_move(self,
                         season_ids_pull: list[int],
                         terrain_card_ids_pull: list[int],
                         monster_card_ids_pull: list[int],
                         ) -> MoveRedis:
        season_id = self._pick_season(season_ids_pull)

        discovery_card_id, discovery_card_type = self. \
            _pick_discovery_card(terrain_card_ids_pull,
                                 monster_card_ids_pull)

        move = MoveDaoRedis(REDIS).start_new_move(
            season_card_id=season_id,
            is_prev_card_ruins=False,
            discovery_card_type=discovery_card_type,
            discovery_card_id=discovery_card_id,
            season_points=0,
        )
        return move

    def _pick_season(self,
                     season_ids_pull: list[int],
                     ) -> int:
        season_id = random.choice(season_ids_pull)
        season_ids_pull.remove(season_id)
        return season_id

    def _pick_discovery_card(self,
                             terrain_card_ids_pull: list[int],
                             monster_card_ids_pull: list[int],
                             ) -> int:

    # total bs, check mechanics of seasons

    def _create_game_model(self,
                           terrain_cards: list[int],
                           monster_cards: list[int],
                           season_ids: list[int],
                           players: list[int],
                           room_id: int,
                           admin_id: int,
                           ) -> GameRedis:
        game = GameRedis(
            id=self._gen_new_id(),
            lobby_id=room_id,
            monster_card_ids_pull=monster_cards,
            season_ids_pull=season_ids,
            terrain_card_ids_pull=terrain_cards,
            player_ids=players,
            admin_id=admin_id,
            current_move_id=None,
        )

        return game

    def init_seasons(self,
                     game: GameRedis,
                     first_move_id: int
                     ) -> dict[ESeasonName, int]:
        """ create season_cards, insert them into redis
         and return their ids """

        objective_card_ids = ObjectiveCardDaoRedis(REDIS). \
            pick_objective_cards()
        season_dao = SeasonDaoRedis(REDIS)

        seasons = dict()
        seasons['spring'] = season_dao.init_season(
            ESeasonName.SPRING,
            objective_card_ids=objective_card_ids[0:2],
            terrain_card_ids=game.terrain_card_ids_pull,
            monster_card_ids={game.monster_card_ids_pull.pop()},
            current_move_id=first_move_id,
        )
        seasons['summer'] = season_dao.init_season()
        seasons['fall'] = season_dao.init_season()
        seasons['summer'] = season_dao.init_season()

        return


class ObjectiveCardDaoRedis(DaoRedisRedis):
    OBJECTIVE_CARD_QUANTITY = 4

    _key_schema = ObjectiveCardKeySchema()
    _transformer = ObjectiveCardTransformer()

    def pick_objective_cards(self):  # it's copypasta!
        card_ids_key = self._key_schema.ids_key
        card_ids = self._redis.smembers(card_ids_key)

        picked_card_ids = random.sample(card_ids,
                                        self.OBJECTIVE_CARD_QUANTITY)
        return picked_card_ids


class TerrainCardDaoRedis(DaoRedisRedis, DaoRedisSQL):
    TERRAIN_CARD_QUANTITY = 20

    _key_schema = TerrainCardKeySchema()
    _transformer = TerrainCardTransformer()
    _model_class = TerrainCardRedis

    def pick_terrain_cards(self):
        card_ids_key = self._key_schema.ids_key
        card_ids = self._redis.smembers(card_ids_key)

        picked_card_ids = random.sample(card_ids,
                                        self.TERRAIN_CARD_QUANTITY)
        return picked_card_ids


class SeasonDaoRedis(DaoRedisRedis):
    _key_schema = SeasonKeySchema()
    _transformer = SeasonTransformer()
    _model_class = SeasonRedis

    ENDING_POINTS_BY_SEASON_NAME = {
        ESeasonName.SPRING: 5,
        ESeasonName.SUMMER: 6,
        ESeasonName.FALL: 7,
        ESeasonName.WINTER: 8,
    }

    def init_season(self,
                    name: ESeasonName,
                    objective_card_ids: Iterable[int],
                    terrain_card_ids: Iterable[int],
                    monster_card_ids: Iterable[int],
                    current_move_id: int | None,
                    ) -> SeasonRedis:
        id = self._gen_new_id()
        points = self.ENDING_POINTS_BY_SEASON_NAME[name]

        season = self._model_class(
            id=id,
            name=name,
            ending_points=points,
            objective_card_ids=set(objective_card_ids),
            terrain_card_ids=set(terrain_card_ids),
            monster_card_ids=set(monster_card_ids),
            current_move_id=current_move_id,
        )
        return season


class MoveDaoRedis(DaoRedisRedis):
    _key_schema = MoveKeySchema()
    _transformer = MoveTransformer()
    _model_class = MoveRedis

    def start_new_move(self,
                       season_card_id: int,
                       is_prev_card_ruins: bool,
                       discovery_card_type: EDiscoveryCardType,
                       discovery_card_id: int,
                       season_points: int | None = None,
                       ):
        id = self._gen_new_id()
        move = self._model_class(
            id=id,
            season_card_id=season_card_id,
            is_prev_card_ruins=is_prev_card_ruins,
            discovery_card_type=discovery_card_type,
            discovery_card_id=discovery_card_id,
            season_points=season_points,
        )
        self.insert_redis_model(move)
        return move


class PlayerDaoRedis(DaoRedisRedis):
    _key_schema = PlayerKeySchema()
    _transformer = PlayerTransformer()


class MonsterCardDaoRedis(DaoRedisRedis, DaoRedisSQL):
    _key_schema = MonsterCardKeySchema()
    _transformer = MonsterCardTransformer()

    def pick_monster_cards(self,
                           ) -> list[int]:
        pass
