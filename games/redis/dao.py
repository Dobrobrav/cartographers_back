import random
from copy import copy
from dataclasses import dataclass
from typing import Iterable, MutableSequence, Sequence, NamedTuple

from cartographers_back.settings import REDIS
from rooms.redis.dao import RoomDaoRedis
from services.redis.model_transformers_base import DictModel
from services.redis.redis_dao_base import DaoRedis, DaoSQL
from .key_schemas import MonsterCardKeySchema, GameKeySchema, SeasonKeySchema, MoveKeySchema, PlayerKeySchema, \
    TerrainCardKeySchema, ObjectiveCardKeySchema
from .model_transformers import MonsterCardTransformer, GameTransformer, SeasonTransformer, MoveTransformer, \
    PlayerTransformer, TerrainCardTransformer, ObjectiveCardTransformer
from .models import SeasonDC, GameData, MoveDC, TerrainCardDC, ESeasonName, EDiscoveryCardType, \
    ObjectiveCardDC


class InitialCards(NamedTuple):
    terrain_card_ids_pull: MutableSequence[int]
    monster_card_ids_pull: MutableSequence[int]
    objective_card_ids_pull: MutableSequence[int]


class GameDaoRedis(DaoRedis):
    MONSTER_CARDS_AMOUNT = 4
    SEASONS_IN_GAME = 4

    _key_schema = GameKeySchema()
    _transformer = GameTransformer()

    # TODO: keep in mind that DictModel is for redis, not necessarily for Response
    # TODO: can I create a base typed dict class for models and inherit from it?
    # TODO: point of redis models is that I operate with them and  transform it into other forms to send it somewhere
    def start_new_game(self,
                       admin_id: int,
                       ) -> DictModel:
        # каждый сезон карты местности перетасовываются, а после хода карта откладывается
        # I think moves should be in season's responsibility

        initial_cards = self._get_initial_cards()

        season_ids = SeasonDaoRedis(REDIS).init_seasons(initial_cards)

        room_id, player_ids = self._get_room_and_players(admin_id)

        game = self._create_game_model(
            initial_cards=initial_cards,
            season_ids=season_ids,
            players=player_ids,
            room_id=room_id,
            admin_id=admin_id,
        )

        return game

    # TODO: need to store id redis if a user have finished his move

    def _get_initial_cards(self):
        terrain_card_ids_pull = TerrainCardDaoRedis(REDIS). \
            pick_terrain_cards()

        monster_card_ids_pull = MonsterCardDaoRedis(REDIS). \
            pick_monster_cards()

        objective_card_ids_pull = ObjectiveCardDaoRedis(REDIS). \
            pick_objective_cards()

        initial_cards = InitialCards(terrain_card_ids_pull,
                                     monster_card_ids_pull,
                                     objective_card_ids_pull)

        return initial_cards

    def _create_game_model(self,
                           initial_cards: InitialCards,
                           season_ids: list[int],
                           players: list[int],
                           room_id: int,
                           admin_id: int,
                           ) -> GameData:
        monster_cards = initial_cards.monster_card_ids_pull
        terrain_cards = initial_cards.terrain_card_ids_pull

        game = GameData(
            id=self._gen_new_id(),
            room_id=room_id,
            monster_card_ids=monster_cards,
            season_ids=season_ids,
            terrain_card_ids=terrain_cards,
            player_ids=players,
            admin_id=admin_id,
            current_season_id=season_ids[0],
        )
        self.insert_dc_model(game)

        return game

    def _get_room_and_players(self,
                              admin_id: int,
                              ) -> tuple[int, list[int]]:
        room_dao = RoomDaoRedis(REDIS)
        player_ids = room_dao.get_player_ids(admin_id)
        room_id = room_dao.get_room_id_by_user_id(admin_id)

        return room_id, player_ids


class ObjectiveCardDaoRedis(DaoRedis):
    OBJECTIVE_CARD_QUANTITY = 4

    _key_schema = ObjectiveCardKeySchema()
    _transformer = ObjectiveCardTransformer()
    _model_class = ObjectiveCardDC

    def pick_objective_cards(self) -> list[int]:  # it's copypasta!
        card_ids_key = self._key_schema.ids_key
        card_ids = self._redis.smembers(card_ids_key)

        picked_card_ids = random.sample(card_ids,
                                        self.OBJECTIVE_CARD_QUANTITY)
        return picked_card_ids


class TerrainCardDaoRedis(DaoRedis, DaoSQL):
    TERRAIN_CARD_QUANTITY = 2

    _key_schema = TerrainCardKeySchema()
    _transformer = TerrainCardTransformer()
    _model_class = TerrainCardDC

    def pick_terrain_cards(self):
        card_ids_key = self._key_schema.ids_key
        card_ids = self._redis.smembers(card_ids_key)

        picked_card_ids = random.sample(card_ids,
                                        self.TERRAIN_CARD_QUANTITY)
        return picked_card_ids


class SeasonDaoRedis(DaoRedis):
    _key_schema = SeasonKeySchema()
    _transformer = SeasonTransformer()
    _model_class = SeasonDC

    ENDING_POINTS_BY_SEASON_NAME = {
        ESeasonName.SPRING: 5,
        ESeasonName.SUMMER: 6,
        ESeasonName.FALL: 7,
        ESeasonName.WINTER: 8,
    }

    def init_seasons(self,
                     initial_cards: InitialCards,
                     ) -> list[int]:
        """ create seasons, insert them into redis
         and return their ids """

        objective_card_ids = initial_cards.objective_card_ids_pull
        terrain_card_ids_pull = initial_cards.terrain_card_ids_pull
        monster_card_ids_pull = initial_cards.monster_card_ids_pull

        seasons = list()
        seasons.append(self.init_season(
            name=ESeasonName.SPRING,
            objective_card_ids=objective_card_ids[0:2],
            terrain_card_ids=terrain_card_ids_pull,
            monster_card_ids=[monster_card_ids_pull.pop()],
            is_first_season=True,
        ))
        seasons.append(self.init_season(
            name=ESeasonName.SUMMER,
            objective_card_ids=objective_card_ids[1:3],
            terrain_card_ids=terrain_card_ids_pull,
            monster_card_ids=[monster_card_ids_pull.pop()],
            # then I'll add monster_cards from prev season
        ))
        seasons.append(self.init_season(
            name=ESeasonName.FALL,
            objective_card_ids=objective_card_ids[2:4],
            terrain_card_ids=terrain_card_ids_pull,
            monster_card_ids=[monster_card_ids_pull.pop()],
        ))
        seasons.append(self.init_season(
            name=ESeasonName.SUMMER,
            objective_card_ids=[objective_card_ids[0],
                                objective_card_ids[4]],
            terrain_card_ids=terrain_card_ids_pull,
            monster_card_ids=[monster_card_ids_pull.pop()],
        ))

        return seasons

    def init_season(self,
                    name: ESeasonName,
                    objective_card_ids: MutableSequence[int],
                    terrain_card_ids: MutableSequence[int],
                    monster_card_ids: MutableSequence[int],
                    is_first_season: bool = False,
                    ) -> int:
        """ create season, insert it and return its id """
        id = self._gen_new_id()
        points = self.ENDING_POINTS_BY_SEASON_NAME[name]

        season_terrain_card_ids = copy(terrain_card_ids)
        season_monster_card_ids = copy(monster_card_ids)

        if is_first_season:
            first_move_id = MoveDaoRedis(REDIS).start_first_move(
                terrain_card_ids=season_terrain_card_ids,
                monster_card_ids=season_monster_card_ids,
            )
        else:
            first_move_id = None

        season = self._model_class(
            id=id,
            name=name,
            ending_points=points,
            objective_card_ids=objective_card_ids,
            terrain_card_ids=terrain_card_ids,
            monster_card_ids=monster_card_ids,
            current_move_id=first_move_id,
        )
        self.insert_dc_model(season)
        return season.id

    def _pick_season(self,
                     season_ids_pull: list[int],
                     ) -> int:
        season_id = random.choice(season_ids_pull)
        season_ids_pull.remove(season_id)
        return season_id


class MoveDaoRedis(DaoRedis):
    _key_schema = MoveKeySchema()
    _transformer = MoveTransformer()
    _model_class = MoveDC

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
        self.insert_dc_model(move)
        return move

    def start_first_move(self,
                         terrain_card_ids: MutableSequence[int],
                         monster_card_ids: MutableSequence[int],
                         ) -> int:
        discovery_card_id, discovery_card_type = self. \
            _pick_discovery_card(terrain_card_ids,
                                 monster_card_ids)

        move = self._model_class(
            id=self._gen_new_id(),
            is_prev_card_ruins=False,
            discovery_card_id=discovery_card_id,
            discovery_card_type=discovery_card_type,
            season_points=0,
        )
        self.insert_dc_model(move)
        return move.id

    def _pick_discovery_card(self,
                             terrain_card_ids: MutableSequence[int],
                             monster_card_ids: MutableSequence[int],
                             ) -> tuple[int, EDiscoveryCardType]:
        terrain_cards_quantity = len(terrain_card_ids)
        monster_cards_quantity = len(monster_card_ids)

        card_type = random.choices(
            population=(EDiscoveryCardType.TERRAIN,
                        EDiscoveryCardType.MONSTER),
            weights=(terrain_cards_quantity,
                     monster_cards_quantity),
            k=1,
        )
        if card_type is EDiscoveryCardType.MONSTER:
            random_monster_card_id = random.choice(monster_card_ids)
            monster_card_ids.remove(random_monster_card_id)
            return random_monster_card_id, card_type

        if card_type is EDiscoveryCardType.TERRAIN:
            random_terrain_card_id = random.choice(terrain_card_ids)
            terrain_card_ids.remove(random_terrain_card_id)
            return random_terrain_card_id, card_type

        raise ValueError('type of card must be either terrain or monster')


# TODO: it will be nice to use deck-type in the future
class PlayerDaoRedis(DaoRedis):
    _key_schema = PlayerKeySchema()
    _transformer = PlayerTransformer()


class MonsterCardDaoRedis(DaoRedis, DaoSQL):
    _key_schema = MonsterCardKeySchema()
    _transformer = MonsterCardTransformer()

    def pick_monster_cards(self,
                           ) -> list[int]:
        pass
