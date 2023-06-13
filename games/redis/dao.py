import random
from copy import copy
from typing import MutableSequence, NamedTuple, Iterable, Optional, TypeAlias, Sequence

from django.contrib.auth.models import User

import services.utils
from cartographers_back.settings import REDIS
from rooms.redis.dao import RoomDaoRedis
from services.redis.redis_dao_base import DaoRedis, DaoFull
from .dict_models import GamePretty, PlayerPretty, SeasonName, URL, ScoreSource, ScoreValue, DiscoveryCardPretty, \
    SeasonsScorePretty, SpringScorePretty, SummerScorePretty, FallScorePretty, WinterScorePretty, ShapePretty, \
    SeasonScorePretty, TaskPretty
from .key_schemas import MonsterCardKeySchema, GameKeySchema, SeasonKeySchema, MoveKeySchema, PlayerKeySchema, \
    TerrainCardKeySchema, ObjectiveCardKeySchema, SeasonsScoreKeySchema, SeasonScoreKeySchema, ShapeKeySchema
from .transformers import MonsterCardTransformer, GameTransformer, SeasonTransformer, MoveTransformer, \
    TerrainCardTransformer, ObjectiveCardTransformer, PlayerTransformer, SeasonsScoreTransformer, \
    SeasonScoreTransformer, ShapeTransformer
from .dc_models import SeasonDC, GameDC, MoveDC, TerrainCardDC, ESeasonName, EDiscoveryCardType, \
    ObjectiveCardDC, PlayerDC, SeasonsScoreDC, SeasonScoreDC, ShapeDC, Field
from ..models import SeasonCardSQL, TERRAIN_STR_TO_NUM, ETerrainTypeAll

PlayerID: TypeAlias = int


class InitialCards(NamedTuple):
    terrain_card_ids: MutableSequence[int]
    monster_card_ids: MutableSequence[int]
    objective_card_ids: MutableSequence[int]


class SeasonCards(NamedTuple):
    spring: SeasonCardSQL
    summer: SeasonCardSQL
    fall: SeasonCardSQL
    winter: SeasonCardSQL


class SeasonPretty(NamedTuple):
    name: str
    url: str


class Neighbors(NamedTuple):
    user_id: int
    left_player_id: int
    player_id: int
    right_player_id: int


class DiscoveryCardDao(DaoFull):

    def get_shape_pretty(self,
                         discovery_card_id: int,
                         ) -> ShapePretty:
        shape_id = self.get_model_attr(
            model_id=discovery_card_id,
            field_name='shape_id',
            converter=int,
        )
        shape_dc: ShapeDC = ShapeDaoRedis(REDIS).fetch_dc_model(shape_id)
        shape_pretty = ShapePretty(
            shape_value=shape_dc.shape_value,
            gives_coin=shape_dc.gives_coin,
        )
        return shape_pretty

    def get_image_url(self,
                      discovery_card_id: int,
                      ) -> str:
        url = self.get_model_attr(
            model_id=discovery_card_id,
            field_name='image_url',
            converter=services.utils.decode_bytes,
        )
        return url


class GameDaoRedis(DaoRedis):
    MONSTER_CARDS_AMOUNT = 4
    SEASONS_IN_GAME = 4

    _key_schema = GameKeySchema()
    _transformer = GameTransformer()

    def start_new_game(self,
                       admin_id: int,
                       ) -> None:
        # каждый сезон карты местности перетасовываются, а после хода карта откладывается
        initial_cards = self._get_initial_cards()
        season_ids = SeasonDaoRedis(REDIS).init_seasons(initial_cards)
        room_id, player_ids = self._get_room_and_players(admin_id)

        game_id = self._create_game_model(
            initial_cards=initial_cards,
            season_ids=season_ids,
            player_ids=player_ids,
            room_id=room_id,
            admin_id=admin_id,
        ).id

        self._add_game_id_by_player_id_index_many(game_id, player_ids)

    def make_move(self,
                  user_id: int,
                  updated_field: MutableSequence[MutableSequence[int]],
                  ) -> None:
        # need to put here checks (maybe)
        self.set_model_attr(
            model_id=PlayerDaoRedis(REDIS).get_player_id_by_user_id(user_id),
            field_name='field',
            value=services.utils.decode_pretty_field(updated_field),
            converter=services.utils.serialize_field,
        )

    def _add_game_id_by_player_id_index_many(self,
                                             game_id: int,
                                             player_ids: Iterable[int],
                                             ) -> None:
        for player_id in player_ids:
            self._add_game_id_by_player_id_index(game_id, player_id)

    def get_game_pretty(self,
                        user_id: int,
                        ) -> GamePretty:
        player_dao = PlayerDaoRedis(REDIS)

        player_id = player_dao.get_player_id_by_user_id(user_id)
        game_id = self._get_game_id_by_player_id(player_id)
        game: GameDC = self.fetch_dc_model(game_id)

        seasons_score_id = player_dao.get_seasons_score_id(player_id)
        seasons_score = SeasonsScoreDao(REDIS).get_seasons_score_pretty(
            seasons_score_id
        )
        season_ids = self._fetch_season_ids(game_id)

        game_pretty = GamePretty(
            id=game_id,
            room_name=RoomDaoRedis(REDIS).get_room_name(game.room_id),
            player_field=player_dao.get_field_pretty(player_id),
            seasons=(season_dao := SeasonDaoRedis(REDIS)).get_seasons_pretty(
                season_ids
            ),
            # tasks=season_dao.get_tasks_pretty(game.season_ids),
            current_season_name=season_dao.get_season_name(
                game.current_season_id
            ),
            players=player_dao.get_players_pretty(game.player_ids),
            discovery_card=(move_dao := MoveDaoRedis(
                REDIS
            )).get_discovery_card_pretty(game_id),
            is_prev_card_ruins=move_dao.fetch_is_prev_card_ruins(
                season_dao.fetch_move_id(game.current_season_id)
            ),
            player_coins=player_dao.get_coins(player_id),
            player_score=self._extract_current_score(seasons_score),
            season_scores=seasons_score,

        )

        return game_pretty

    def _fetch_season_ids(self,
                          game_id: int,
                          ) -> list[int]:
        season_ids = self.get_model_attr(
            model_id=game_id,
            field_name='season_ids',
        )
        return season_ids

    @staticmethod
    def _extract_current_score(seasons_score: SeasonsScorePretty,
                               ) -> int:
        spring_total = seasons_score['spring_score']['total']
        summer_total = seasons_score['summer_score']['total']
        fall_total = seasons_score['fall_score']['total']
        winter_total = seasons_score['winter_score']['total']

        return spring_total + summer_total + fall_total + winter_total

    def _get_game_id_by_player_id(self,
                                  player_id: int,
                                  ) -> int:
        key = self._key_schema.game_id_by_player_id_index_key
        game_id = services.utils.deserialize(
            self._redis.hget(key, player_id)
        )
        return game_id

    def _get_game_id_by_room_id(self,
                                room_id: int,
                                ) -> int:
        key = self._key_schema.game_id_by_room_id_index_key
        game_id = int(self._redis.hget(key, room_id))
        return game_id

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
            id=(game_id := self._gen_new_id()),
            room_id=room_id,
            monster_card_ids=monster_card_ids,
            season_ids=season_ids,
            terrain_card_ids=terrain_card_ids,
            player_ids=player_ids,
            admin_id=admin_id,
            current_season_id=season_ids[0],
        )
        self.insert_dc_model(game)
        self._add_game_id_by_room_id_index(room_id, game_id)

        return game

    def _add_game_id_by_room_id_index(self,
                                      room_id: int,
                                      game_id: int,
                                      ) -> None:
        key = self._key_schema.game_id_by_room_id_index_key
        self._redis.hset(key, room_id, game_id)

    def _get_room_and_players(self,
                              admin_id: int,
                              ) -> tuple[int, list[int]]:
        user_ids = (room_dao := RoomDaoRedis(REDIS)).get_user_ids(admin_id)
        field = self._gen_field()
        player_ids = PlayerDaoRedis(REDIS).init_players(user_ids, field)
        room_id = room_dao.get_room_id_by_user_id(admin_id)

        return room_id, player_ids

    def _add_game_id_by_player_id_index(self,
                                        game_id: int,
                                        player_id: int,
                                        ) -> None:
        key = self._key_schema.game_id_by_player_id_index_key
        self._redis.hset(key, player_id, game_id)

    def _gen_field(self) -> Field:
        blank_field = [[ETerrainTypeAll.BLANK] * 11] * 11
        return blank_field


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


class TerrainCardDaoRedis(DiscoveryCardDao):
    TERRAIN_CARD_QUANTITY = 2

    _key_schema = TerrainCardKeySchema()
    _transformer = TerrainCardTransformer()
    _model_class = TerrainCardDC

    def get_terrain_pretty(self,
                           terrain_card_id: int,
                           ) -> int:
        terrain = self.get_model_attr(
            model_id=terrain_card_id,
            field_name='terrain',
            converter=services.utils.decode_bytes
        )
        terrain_pretty = TERRAIN_STR_TO_NUM[terrain]
        return terrain_pretty

    def get_additional_terrain_pretty(self,
                                      terrain_card_id: int,
                                      ) -> Optional[int]:
        additional_terrain = self.get_model_attr(
            model_id=terrain_card_id,
            field_name='additional_terrain',
            converter=services.utils.decode_bytes,
        )
        # if no add_terrain, then return None
        additional_terrain_pretty = (additional_terrain
                                     and TERRAIN_STR_TO_NUM[additional_terrain])
        return additional_terrain_pretty

    def get_additional_shape(self,
                             terrain_card_id: int,
                             ) -> Optional[str]:
        additional_shape = self.get_model_attr(
            model_id=terrain_card_id,
            field_name='additional_shape',
            converter=services.utils.decode_bytes,
        )
        return additional_shape

    def pick_terrain_cards(self):
        card_ids_key = self._key_schema.ids_key
        card_ids = [int(id) for id in self._redis.smembers(card_ids_key)]

        picked_card_ids = random.sample(card_ids,
                                        self.TERRAIN_CARD_QUANTITY)
        return picked_card_ids


class ShapeDaoRedis(DaoFull):
    _key_schema = ShapeKeySchema()
    _transformer = ShapeTransformer()
    _model_class = ShapeDC


class SeasonDaoRedis(DaoRedis):
    _key_schema = SeasonKeySchema()
    _transformer = SeasonTransformer()
    _model_class = SeasonDC

    def fetch_move_id(self,
                      season_id: int,
                      ) -> int:
        key = self._key_schema.get_hash_key(season_id)
        move_id = int(self._redis.hget(key, 'current_move_id'))
        return move_id

    # def get_tasks_pretty(self,
    #                      season_ids: Iterable[int],
    #                      ) -> list[TaskPretty]:
    #     objective_card_ids = self._get_objective_card_ids(season_ids)
    #     tasks_pretty = [
    #
    #         for
    #     ]
    #
    # def _get_objective_card_ids(self,):

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
            name=ESeasonName.WINTER,
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

    def get_seasons_pretty(self,
                           season_ids: Iterable[int],
                           ) -> dict[SeasonName: SeasonPretty]:
        seasons = {
            (season := self.get_season_pretty(season_id)).name: season.url
            for season_id in season_ids
        }
        return seasons

    def get_season_pretty(self,
                          season_id: int,
                          ) -> SeasonPretty:
        name = self.get_season_name(season_id)
        url = self.get_season_url(season_id)
        return SeasonPretty(name, url)

    def get_season_url(self,
                       season_id: int,
                       ) -> str:
        key = self._key_schema.get_hash_key(season_id)
        url = self._redis.hget(key, 'image_url').decode('utf-8')
        return url

    def get_season_name(self,
                        season_id: int,
                        ) -> str:
        print(season_id)
        season_name = self.get_model_attr(
            model_id=season_id,
            field_name='name',
            converter=services.utils.decode_bytes,
        )
        if season_name is None:
            raise ValueError('season_name must not be None')
        return season_name

    def get_season_score_pretty(self,
                                season_id: int,
                                ):
        ...

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
                       is_prev_card_ruins: bool,
                       discovery_card_type: EDiscoveryCardType,
                       discovery_card_id: int,
                       season_points: Optional[int] = None,
                       ):
        id = self._gen_new_id()
        move = self._model_class(
            id=id,
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

    def get_discovery_card_pretty(self,
                                  move_id: int,
                                  ) -> DiscoveryCardPretty:
        discovery_card_pretty = DiscoveryCardPretty(
            image=self._fetch_card_image_url(move_id),
            is_anomaly=self._check_card_is_anomaly(move_id),
            terrain_int=self._fetch_card_terrain(move_id),
            additional_terrain_int=self._fetch_card_additional_terrain(move_id),
            shape=self._get_card_shape_pretty(move_id),
            additional_shape=self._fetch_card_additional_shape(move_id),
        )
        # TODO: replace 'additional_' with extra_
        return discovery_card_pretty

    def _check_card_is_anomaly(self,
                               move_id: int,
                               ) -> bool:
        type = self._fetch_discovery_card_type(move_id)
        return type == 'anomaly'

    def _fetch_card_terrain(self,
                            move_id: int,
                            ) -> int:
        type = self._fetch_discovery_card_type(move_id)
        match type:
            case 'terrain':
                terrain = TerrainCardDaoRedis(REDIS).get_terrain_pretty(
                    terrain_card_id=self._fetch_discovery_card_id(move_id)
                )
            case 'monster':
                terrain = TERRAIN_STR_TO_NUM['monster']
            case _:
                raise ValueError('discovery card type must be '
                                 'either "terrain" or "monster"')

        return terrain

    def _fetch_card_additional_terrain(self,
                                       move_id: int,
                                       ) -> Optional[int]:
        type = self._fetch_discovery_card_type(move_id)
        if type != 'terrain':
            return None

        terrain = TerrainCardDaoRedis(REDIS).get_additional_terrain_pretty(
            terrain_card_id=self._fetch_discovery_card_id(move_id)
        )
        return terrain

    def _fetch_discovery_card_id(self,
                                 move_id: int,
                                 ) -> int:
        id = self.get_model_attr(
            model_id=move_id,
            field_name='discovery_card_id',
            converter=int,
        )
        return id

    def _get_card_shape_pretty(self,
                               move_id: int,
                               ) -> ShapePretty:
        type = self._fetch_discovery_card_type(move_id)
        card_id = self._fetch_discovery_card_id(move_id)

        match type:
            case 'terrain':
                card_dao = TerrainCardDaoRedis(REDIS)
            case 'monster':
                card_dao = MonsterCardDaoRedis(REDIS)
            case _:
                raise ValueError('type must be either "monster" or "terrain"')

        shape = card_dao.get_shape_pretty(card_id)

        return shape

    def _fetch_card_additional_shape(self,
                                     move_id: int,
                                     ) -> Optional[str]:
        type = self._fetch_discovery_card_type(move_id)
        if type != 'terrain':
            raise ValueError('must be terrain type')

        additional_shape = TerrainCardDaoRedis(REDIS).get_additional_shape(
            self._fetch_discovery_card_id(move_id)
        )

        return additional_shape

    def _fetch_is_prev_card_ruins(self,
                                  move_id: int,
                                  ) -> bool:
        res = self.get_model_attr(
            model_id=move_id,
            field_name='is_prev_card_ruins',
            converter=lambda x: bool(int(x)),
        )
        return res

    def _fetch_card_image_url(self,
                              move_id: int,
                              ) -> URL:
        type = self._fetch_discovery_card_type(move_id)

        match type:  # why not use Literal for card_type everywhere
            case 'terrain':
                discovery_card_dao = TerrainCardDaoRedis(REDIS)
            case 'monster':
                discovery_card_dao = MonsterCardDaoRedis(REDIS)
            case _:
                raise ValueError('Type of discovery card must be either '
                                 '"terrain" or "monster"')

        res = discovery_card_dao.get_image_url(
            self._fetch_discovery_card_id(move_id)
        )

        return res

    def _fetch_discovery_card_type(self,
                                   move_id: int,
                                   ) -> str:
        type = self.get_model_attr(
            model_id=move_id,
            field_name='discovery_card_type',
            converter=services.utils.decode_bytes,
        )
        return type

    def fetch_is_prev_card_ruins(self,
                                 move_id: int,
                                 ) -> bool:
        is_prev_card_ruins = self.get_model_attr(
            model_id=move_id,
            field_name='is_prev_card_ruins',
            converter=lambda x: bool(int(x)),
        )
        return is_prev_card_ruins


# TODO: it will be nice to use deck-type structure for cards in the future
class PlayerDaoRedis(DaoRedis):
    _key_schema = PlayerKeySchema()
    _transformer = PlayerTransformer()
    _model_class = PlayerDC

    def get_players_pretty(self,
                           player_ids: Iterable[int],
                           ) -> list[PlayerPretty]:
        players = [
            self._get_player_pretty(player_id)
            for player_id in player_ids
        ]
        return players

    def init_players(self,
                     user_ids: Sequence[int],
                     field: Field,
                     ) -> list[int]:
        neighbors_lst = self._get_neighbors_lst(user_ids)
        player_ids = [
            self._init_player(neighbors, field)
            for neighbors in neighbors_lst
        ]
        return player_ids

    def get_seasons_score_id(self,
                             player_id: int,
                             ) -> int:
        id = self.get_model_attr(
            model_id=player_id,
            field_name='seasons_score_id',
            converter=int,
        )
        return id

    def get_player_id_by_user_id(self,
                                 user_id: int,
                                 ) -> int:
        key = self._key_schema.player_id_by_user_id_index_key
        player_id = int(self._redis.hget(key, user_id))
        return player_id

    def _get_neighbors_lst(self,
                           user_ids: Sequence[int],
                           ) -> list[Neighbors]:
        player_ids = self._gen_new_ids(quantity=len(user_ids))
        neighbors_lst = []
        for user_id, (i, player_id) in zip(user_ids, enumerate(player_ids)):
            right_player_id_index = (0 if self._is_last_index(player_ids, i)
                                     else i + 1)
            neighbors = Neighbors(
                user_id=user_id,
                left_player_id=player_ids[i - 1],
                player_id=player_id,
                right_player_id=player_ids[right_player_id_index],
            )
            neighbors_lst.append(neighbors)

        return neighbors_lst

    @staticmethod
    def _is_last_index(seq: Sequence,
                       index: int,
                       ) -> bool:
        return index == len(seq) - 1

    def _init_player(self,
                     neighbors: Neighbors,
                     field: Field
                     ) -> int:
        seasons_score_id = SeasonsScoreDao(REDIS).init_seasons_score()  # create seasons for players
        player_dc = self._create_model(neighbors, field, seasons_score_id)
        self.insert_dc_model(player_dc)
        self._add_player_id_by_user_id_index(player_dc.id, neighbors.user_id)
        return player_dc.id

    def _add_player_id_by_user_id_index(self,
                                        player_id: int,
                                        user_id: int,
                                        ) -> None:
        key = self._key_schema.player_id_by_user_id_index_key
        self._redis.hset(key, user_id, player_id)

    def _create_model(self,
                      neighbors: Neighbors,
                      field: Field,
                      seasons_score_id: int,
                      ) -> PlayerDC:
        player_dc = self._model_class(
            id=neighbors.player_id,
            user_id=neighbors.user_id,
            field=field,
            left_player_id=neighbors.left_player_id,
            right_player_id=neighbors.right_player_id,
            coins=0,
            seasons_score_id=seasons_score_id,
            finished_move=False,
        )
        return player_dc

    def _get_player_pretty(self,
                           player_id: int,
                           ) -> PlayerPretty:
        return PlayerPretty(
            id=player_id,
            name=self.get_name(player_id),
            score=self.get_score_total(player_id)
        )

    def get_field_pretty(self,
                         player_id: int,
                         ) -> list[list[int]]:
        field_pretty = self.get_model_attr(
            model_id=player_id,
            field_name='field',
            converter=lambda x: self._make_field_pretty(
                services.utils.deserialize_field(x)
            ),
        )
        return field_pretty

    @staticmethod
    def _make_field_pretty(field: Field,
                           ) -> Field:
        field_pretty = [
            [TERRAIN_STR_TO_NUM[cell.value] for cell in row]
            for row in field
        ]
        return field_pretty

    def get_score_total(self,
                        player_id: int,
                        ) -> int:
        seasons_score_id = self._get_seasons_score_id(player_id)
        total = SeasonsScoreDao(REDIS).get_score(seasons_score_id)
        return total

    def _get_seasons_score_id(self,
                              player_id: int,
                              ) -> int:
        seasons_score_id = self.get_model_attr(
            model_id=player_id,
            field_name='seasons_score_id',
            converter=int,
        )
        return seasons_score_id

    def get_coins(self,
                  player_id: int,
                  ) -> int:
        key = self._key_schema.get_hash_key(player_id)
        score = int(self._redis.hget(key, 'coins'))
        return score

    def get_name(self,
                 player_id: int,
                 ) -> str:
        user_id = self._get_user_id(player_id)
        name = User.objects.get(pk=user_id).username
        return name

    def _get_user_id(self,
                     player_id: int,
                     ) -> int:
        user_id = self.get_model_attr(
            model_id=player_id,
            field_name='user_id',
            converter=int,
        )
        return user_id


class SeasonsScoreDao(DaoRedis):
    _key_schema = SeasonsScoreKeySchema()
    _transformer = SeasonsScoreTransformer()
    _model_class = SeasonsScoreDC

    def init_seasons_score(self) -> int:
        season_score_dao = SeasonScoreDao(REDIS)
        season_score = self._model_class(
            id=self._gen_new_id(),
            spring_score_id=season_score_dao.init_season_score(),
            summer_score_id=season_score_dao.init_season_score(),
            fall_score_id=season_score_dao.init_season_score(),
            winter_score_id=season_score_dao.init_season_score(),
            coins=0,
            total=0,
        )
        self.insert_dc_model(season_score)

        return season_score.id

    def get_seasons_score_pretty(self,
                                 seasons_score_id: int,
                                 ) -> SeasonsScorePretty:
        ids = self._get_season_score_ids(seasons_score_id)
        dao = SeasonScoreDao(REDIS)

        res = SeasonsScorePretty(
            spring_score=dao.get_season_score_pretty(ids[0]),
            summer_score=dao.get_season_score_pretty(ids[1]),
            fall_score=dao.get_season_score_pretty(ids[2]),
            winter_score=dao.get_season_score_pretty(ids[3]),
        )
        return res

    def get_score(self,
                  seasons_score_id: int,
                  ) -> int:
        season_score_ids = self._get_season_score_ids(seasons_score_id)
        total = SeasonScoreDao(REDIS).get_seasons_score_total(season_score_ids)
        return total

    def _get_season_score_ids(self,
                              seasons_score_id: int,
                              ) -> list[int]:
        season_score_ids = [
            self._get_season_score_id(seasons_score_id,
                                      ESeasonName.SPRING),
            self._get_season_score_id(seasons_score_id,
                                      ESeasonName.SUMMER),
            self._get_season_score_id(seasons_score_id,
                                      ESeasonName.FALL),
            self._get_season_score_id(seasons_score_id,
                                      ESeasonName.WINTER),
        ]
        return season_score_ids

    def _get_total(self,
                   seasons_score_id: int,
                   ) -> int:
        total = self.get_model_attr(
            model_id=seasons_score_id,
            field_name='total',
            converter=int
        )
        return total

    def _get_coins(self,
                   seasons_score_id: int,
                   ) -> int:
        coins = self.get_model_attr(
            model_id=seasons_score_id,
            field_name='coins',
            converter=int
        )
        return coins

    def _get_spring_score_pretty(self,
                                 seasons_score_id: int,
                                 ) -> SpringScorePretty:
        season_score = self._get_generic_season_score(
            seasons_score_id=seasons_score_id,
            season=ESeasonName.SPRING,
        )

        spring_score_pretty = SpringScorePretty(
            from_coins=season_score.from_coins,
            monsters=season_score.monsters,
            total=season_score.total,
            A=season_score.from_first_task,
            B=season_score.from_second_task,
        )

        return spring_score_pretty

    def _get_summer_score_pretty(self,
                                 seasons_score_id: int,
                                 ) -> SummerScorePretty:
        generic_season_score = self._get_generic_season_score(
            seasons_score_id=seasons_score_id,
            season=ESeasonName.SUMMER,
        )

        summer_score_pretty = SummerScorePretty(
            from_coins=generic_season_score.from_coins,
            monsters=generic_season_score.monsters,
            total=generic_season_score.total,
            B=generic_season_score.from_first_task,
            C=generic_season_score.from_second_task,
        )

        return summer_score_pretty

    def _get_fall_score_pretty(self,
                               seasons_score_id: int,
                               ) -> FallScorePretty:
        season_score = self._get_generic_season_score(
            seasons_score_id=seasons_score_id,
            season=ESeasonName.FALL,
        )

        fall_score_pretty = FallScorePretty(
            from_coins=season_score.from_coins,
            monsters=season_score.monsters,
            total=season_score.total,
            C=season_score.from_first_task,
            D=season_score.from_second_task,
        )

        return fall_score_pretty

    def _get_winter_score_pretty(self,
                                 seasons_score_id: int,
                                 ) -> WinterScorePretty:
        season_score = self._get_generic_season_score(
            seasons_score_id=seasons_score_id,
            season=ESeasonName.WINTER,
        )

        winter_score_pretty = WinterScorePretty(
            from_coins=season_score.from_coins,
            monsters=season_score.monsters,
            total=season_score.total,
            D=season_score.from_first_task,
            A=season_score.from_second_task,
        )

        return winter_score_pretty

    def _get_season_score_id(self,
                             seasons_score_id: int,
                             season: ESeasonName):
        season_score_id = self.get_model_attr(
            model_id=seasons_score_id,
            field_name=f'{season.value}_score_id',
            converter=int,
        )
        return season_score_id


class SeasonScoreDao(DaoRedis):
    _key_schema = SeasonScoreKeySchema()
    _transformer = SeasonScoreTransformer()
    _model_class = SeasonScoreDC

    def init_season_score(self) -> int:
        season = self._model_class(
            id=self._gen_new_id(),
            from_first_task=0,
            from_second_task=0,
            from_coins=0,
            monsters=0,
            total=0,
        )
        self.insert_dc_model(season)

        return season.id

    def get_seasons_score_total(self,
                                season_score_ids: Iterable[int],
                                ) -> int:
        total = sum(
            self._get_season_score_total(season_score_id)
            for season_score_id in season_score_ids
        )
        return total

    def get_season_score_pretty(self,
                                season_score_id: int,
                                ) -> SeasonScorePretty:
        season_score: SeasonScoreDC = self.fetch_dc_model(season_score_id)

        season_score_pretty = SeasonScorePretty(
            from_coins=season_score.from_coins,
            monsters=season_score.monsters,
            total=season_score.total,
            from_first_task=season_score.from_first_task,
            from_second_task=season_score.from_second_task,
        )

        return season_score_pretty

    def _get_season_score_total(self,
                                season_score_id: int,
                                ) -> int:
        total = self.get_model_attr(
            model_id=season_score_id,
            field_name='total',
            converter=int,
        )
        return total


class MonsterCardDaoRedis(DiscoveryCardDao):
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
