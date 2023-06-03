import random
from copy import copy
from typing import MutableSequence, NamedTuple

from cartographers_back.settings import REDIS
from rooms.redis.dao import RoomDaoRedis
from services.redis.transformers_base import DictModel
from services.redis.redis_dao_base import DaoRedis, DaoFull, DaoBase
from .key_schemas import MonsterCardKeySchema, GameKeySchema, SeasonKeySchema, MoveKeySchema, PlayerKeySchema, \
    TerrainCardKeySchema, ObjectiveCardKeySchema
from .transformers import MonsterCardTransformer, GameTransformer, SeasonTransformer, MoveTransformer, \
    TerrainCardTransformer, ObjectiveCardTransformer, PlayerTransformer
from .dc_models import SeasonDC, GameDC, MoveDC, TerrainCardDC, ESeasonName, EDiscoveryCardType, \
    ObjectiveCardDC
from ..models import SeasonCardSQL


class InitialCards(NamedTuple):
    terrain_card_ids: MutableSequence[int]
    monster_card_ids: MutableSequence[int]
    objective_card_ids: MutableSequence[int]


class SeasonCards(NamedTuple):
    spring: SeasonCardSQL
    summer: SeasonCardSQL
    fall: SeasonCardSQL
    winter: SeasonCardSQL


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
        initial_cards = self._get_initial_cards()

        season_ids = SeasonDaoRedis(REDIS).init_seasons(initial_cards)

        room_id, player_ids = self._get_room_and_players(admin_id)

        game = self._create_game_model(
            initial_cards=initial_cards,
            season_ids=season_ids,
            player_ids=player_ids,
            room_id=room_id,
            admin_id=admin_id,
        )

        return game

    # TODO: need to store in redis attr indicating if user has finished his move

    @staticmethod
    def _get_initial_cards():
        terrain_card_ids = TerrainCardDaoRedis(REDIS). \
            pick_terrain_cards()

        monster_card_ids = MonsterCardDaoRedis(REDIS). \
            pick_monster_cards()

        objective_card_ids = ObjectiveCardDaoRedis(REDIS). \
            pick_objective_cards()

        initial_cards = InitialCards(terrain_card_ids,
                                     monster_card_ids,
                                     objective_card_ids)

        return initial_cards

    def _create_game_model(self,
                           initial_cards: InitialCards,
                           season_ids: list[int],
                           player_ids: list[int],
                           room_id: int,
                           admin_id: int,
                           ) -> GameDC:
        monster_card_ids = initial_cards.monster_card_ids
        terrain_card_ids = initial_cards.terrain_card_ids

        game = GameDC(
            id=self._gen_new_id(),
            room_id=room_id,
            monster_card_ids=monster_card_ids,
            season_ids=season_ids,
            terrain_card_ids=terrain_card_ids,
            player_ids=player_ids,
            admin_id=admin_id,
            current_season_id=season_ids[0],
        )
        self.insert_dc_model(game)

        return game

    @staticmethod
    def _get_room_and_players(admin_id: int,
                              ) -> tuple[int, list[int]]:
        room_dao = RoomDaoRedis(REDIS)
        player_ids = room_dao.get_player_ids(admin_id)
        room_id = room_dao.get_room_id_by_user_id(admin_id)

        return room_id, player_ids


class ObjectiveCardDaoRedis(DaoFull):
    OBJECTIVE_CARD_QUANTITY = 4

    _key_schema = ObjectiveCardKeySchema()
    _transformer = ObjectiveCardTransformer()
    _model_class = ObjectiveCardDC

    def pick_objective_cards(self) -> list[int]:  # it's copypasta!
        card_ids_key = self._key_schema.ids_key
        card_ids = [int(id) for id in self._redis.smembers(card_ids_key)]

        picked_card_ids = random.sample(card_ids,
                                        self.OBJECTIVE_CARD_QUANTITY)
        return picked_card_ids


class TerrainCardDaoRedis(DaoFull):
    TERRAIN_CARD_QUANTITY = 2

    _key_schema = TerrainCardKeySchema()
    _transformer = TerrainCardTransformer()
    _model_class = TerrainCardDC

    def pick_terrain_cards(self):
        card_ids_key = self._key_schema.ids_key
        card_ids = [int(id) for id in self._redis.smembers(card_ids_key)]

        picked_card_ids = random.sample(card_ids,
                                        self.TERRAIN_CARD_QUANTITY)
        return picked_card_ids


class SeasonDaoRedis(DaoRedis):
    _key_schema = SeasonKeySchema()
    _transformer = SeasonTransformer()
    _model_class = SeasonDC

    def init_seasons(self,
                     initial_cards: InitialCards,
                     ) -> list[int]:
        print(initial_cards)
        """ create seasons, insert them into redis
         and return their ids """

        objective_card_ids = initial_cards.objective_card_ids
        terrain_card_ids = initial_cards.terrain_card_ids
        monster_card_ids = initial_cards.monster_card_ids

        season_cards = self._get_season_cards()

        seasons = list()
        seasons.append(self.init_season(
            name=ESeasonName.SPRING,
            season_card=season_cards.spring,
            objective_card_ids=objective_card_ids[0:2],
            terrain_card_ids=self._shuffle_cards(terrain_card_ids),
            monster_card_ids=[monster_card_ids.pop()],
            is_first_season=True,
        ))
        seasons.append(self.init_season(
            name=ESeasonName.SUMMER,
            season_card=season_cards.summer,
            objective_card_ids=objective_card_ids[1:3],
            terrain_card_ids=self._shuffle_cards(terrain_card_ids),
            monster_card_ids=[monster_card_ids.pop()],
            # then I'll add monster_card(s) from prev season
        ))
        seasons.append(self.init_season(
            name=ESeasonName.FALL,
            season_card=season_cards.fall,
            objective_card_ids=objective_card_ids[2:4],
            terrain_card_ids=self._shuffle_cards(terrain_card_ids),
            monster_card_ids=[monster_card_ids.pop()],
        ))
        seasons.append(self.init_season(
            name=ESeasonName.SUMMER,
            season_card=season_cards.winter,
            objective_card_ids=[objective_card_ids[0],
                                objective_card_ids[3]],
            terrain_card_ids=self._shuffle_cards(objective_card_ids),
            monster_card_ids=[monster_card_ids.pop()],
        ))

        return seasons

    def init_season(self,
                    name: ESeasonName,
                    season_card: SeasonCardSQL,
                    objective_card_ids: MutableSequence[int],
                    terrain_card_ids: MutableSequence[int],
                    monster_card_ids: MutableSequence[int],
                    is_first_season: bool = False,
                    ) -> int:
        """ create season, insert it and return its id """
        first_move_id = self._start_first_move(
            terrain_card_ids, monster_card_ids
        ) if is_first_season else None

        season = self._model_class(
            id=self._gen_new_id(),
            name=name,
            image_url=season_card.image.url,
            points_to_end=season_card.points_to_end,
            objective_card_ids=objective_card_ids,
            terrain_card_ids=terrain_card_ids,
            monster_card_ids=monster_card_ids,
            current_move_id=first_move_id,
        )
        self.insert_dc_model(season)

        return season.id

    @staticmethod
    def _get_season_cards() -> SeasonCards:
        cards = SeasonCards(
            spring=SeasonCardSQL.objects.get(name__iexact='весна'),
            summer=SeasonCardSQL.objects.get(name__iexact='лето'),
            fall=SeasonCardSQL.objects.get(name__iexact='осень'),
            winter=SeasonCardSQL.objects.get(name__iexact='зима'),
        )
        return cards

    def _start_first_move(self,
                          terrain_card_ids: MutableSequence[int],
                          monster_card_ids: MutableSequence[int],
                          ):
        discovery_card_id, discovery_card_type = self. \
            _pick_discovery_card(terrain_card_ids, monster_card_ids)

        first_move_id = MoveDaoRedis(REDIS).start_first_move(
            discovery_card_id=discovery_card_id,
            discovery_card_type=discovery_card_type,
        )
        return first_move_id

    @staticmethod
    def _pick_discovery_card(terrain_card_ids: MutableSequence[int],
                             monster_card_ids: MutableSequence[int],
                             ) -> tuple[int, EDiscoveryCardType]:
        terrain_cards_quantity = len(terrain_card_ids)
        monster_cards_quantity = len(monster_card_ids)

        card_type = random.choices(
            population=(EDiscoveryCardType.TERRAIN,
                        EDiscoveryCardType.MONSTER),
            weights=(terrain_cards_quantity,
                     monster_cards_quantity),
        )[0]

        if card_type is EDiscoveryCardType.MONSTER:
            random_monster_card_id = random.choice(monster_card_ids)
            monster_card_ids.remove(random_monster_card_id)
            return random_monster_card_id, card_type

        if card_type is EDiscoveryCardType.TERRAIN:
            random_terrain_card_id = random.choice(terrain_card_ids)
            terrain_card_ids.remove(random_terrain_card_id)
            return random_terrain_card_id, card_type

        raise ValueError('type of card must be either terrain or monster')

    @staticmethod
    def _shuffle_cards(cards: MutableSequence[int],
                       ) -> MutableSequence[int]:
        """ return shuffled copy of cards """
        cards = copy(cards)
        random.shuffle(cards)

        return cards

    @staticmethod
    def _pick_season(season_ids_pull: list[int],
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
                         discovery_card_id: int,
                         discovery_card_type: EDiscoveryCardType,
                         ) -> int:
        move = self._model_class(
            id=self._gen_new_id(),
            is_prev_card_ruins=False,
            discovery_card_id=discovery_card_id,
            discovery_card_type=discovery_card_type,
            season_points=0,
        )
        self.insert_dc_model(move)
        return move.id


# TODO: it will be nice to use deck-type in the future
class PlayerDaoRedis(DaoRedis):
    _key_schema = PlayerKeySchema()
    _transformer = PlayerTransformer()


class MonsterCardDaoRedis(DaoFull):
    _key_schema = MonsterCardKeySchema()
    _transformer = MonsterCardTransformer()
    MONSTER_CARD_QUANTITY = 4

    def pick_monster_cards(self,
                           ) -> list[int]:
        card_ids_key = self._key_schema.ids_key
        card_ids = [int(id) for id in self._redis.smembers(card_ids_key)]

        picked_card_ids = random.sample(card_ids,
                                        self.MONSTER_CARD_QUANTITY)
        return picked_card_ids
