import random
from copy import copy
from typing import MutableSequence, NamedTuple, Iterable, Optional, TypeAlias, Sequence, overload, Literal

from django.contrib.auth.models import User

import services.utils
from cartographers_back.settings import R
from rooms.redis.dao import RoomDao
from services.redis.base.redis_dao_base import DaoRedis, DaoFull
from .dict_models import GamePretty, PlayerPretty, SeasonName, URL, DiscoveryCardPretty, \
    SeasonsScorePretty, SpringScorePretty, SummerScorePretty, FallScorePretty, WinterScorePretty, ShapePretty, \
    SeasonScorePretty
from .key_schemas import MonsterCardKeySchema, GameKeySchema, SeasonKeySchema, MoveKeySchema, PlayerKeySchema, \
    TerrainCardKeySchema, ObjectiveCardKeySchema, SeasonsScoreKeySchema, SeasonScoreKeySchema, ShapeKeySchema
from .converters import MonsterCardConverter, GameConverter, SeasonConverter, MoveConverter, \
    TerrainCardConverter, ObjectiveCardConverter, PlayerConverter, SeasonsScoreConverter, \
    SeasonScoreConverter, ShapeConverter
from .dc_models import SeasonDC, GameDC, MoveDC, TerrainCardDC, ESeasonName, EDiscoveryCardType, \
    ObjectiveCardDC, PlayerDC, SeasonsScoreDC, SeasonScoreDC, ShapeDC
from .. import utils
from ..common import ETerrainTypeAll, TERRAIN_STR_TO_NUM, FieldPretty, Field, BLANK_FIELD
from ..models import SeasonCardSQL
import games.utils

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

    def fetch_shape_pretty(self,
                           discovery_card_id: int,
                           ) -> ShapePretty:
        shape_id = self._fetch_model_attr(
            model_id=discovery_card_id,
            field_name='shape_id',
            converter=int,
        )
        services.utils.validate_not_none(shape_id)

        shape_dc: ShapeDC = ShapeDaoRedis(R).fetch_dc_model(shape_id)
        shape_pretty = ShapePretty(
            shape_value=shape_dc.shape_value,
            gives_coin=shape_dc.gives_coin,
        )
        return shape_pretty

    def fetch_image_url(self,
                        discovery_card_id: int,
                        ) -> str:
        url = self._fetch_model_attr(
            model_id=discovery_card_id,
            field_name='image_url',
            converter=services.utils.decode_bytes,
        )
        services.utils.validate_not_none(url)

        return url

    def pick_card(self,
                  terrain_card_ids: MutableSequence[int],
                  monster_card_ids: MutableSequence[int],
                  is_ruins_allowed: bool,
                  ) -> tuple[int, EDiscoveryCardType]:
        card_type = self._pick_discovery_card_type(
            terrain_cards_quantity=len(terrain_card_ids),
            monster_cards_quantity=len(monster_card_ids),
        )

        if card_type is EDiscoveryCardType.MONSTER:
            card_id = self._pick_card_id(monster_card_ids)
        elif card_type is EDiscoveryCardType.TERRAIN:
            card_id = TerrainCardDao(R).pick_terrain_card_id(
                terrain_card_ids, is_ruins_allowed,
            )
        else:
            raise ValueError('type of card must be either terrain or monster')

        return card_id, card_type

    def pick_card_and_is_on_ruins(self,
                                  terrain_card_ids: MutableSequence[int],
                                  monster_card_ids: MutableSequence[int],
                                  is_on_ruins_allowed: bool,
                                  ):
        is_on_ruins = False
        card_id, discovery_card_type = self.pick_card(
            terrain_card_ids=terrain_card_ids,
            monster_card_ids=monster_card_ids,
            is_ruins_allowed=is_on_ruins_allowed,
        )

        if is_on_ruins_allowed and MoveDao(R).check_card_is_ruins(card_id):
            is_on_ruins = True
            card_id, discovery_card_type = self.pick_card(
                terrain_card_ids=terrain_card_ids,
                monster_card_ids=monster_card_ids,
                is_ruins_allowed=False,
            )
        return card_id, discovery_card_type, is_on_ruins

    @staticmethod
    def _pick_discovery_card_type(terrain_cards_quantity: int,
                                  monster_cards_quantity: int,
                                  ) -> ...:
        random_type = random.choices(
            population=(EDiscoveryCardType.TERRAIN,
                        EDiscoveryCardType.MONSTER),
            weights=(terrain_cards_quantity,
                     monster_cards_quantity),
        )[0]
        return random_type

    @staticmethod
    def _pick_card_id(card_ids: MutableSequence[int],
                      ) -> int:
        random_card_id = random.choice(card_ids)
        print('::::::', card_ids, random_card_id)
        return random_card_id


class GameDao(DaoRedis):
    MONSTER_CARDS_AMOUNT = 4
    SEASONS_IN_GAME = 4

    _key_schema = GameKeySchema()
    _converter = GameConverter()

    def try_init_game(self,
                      initiator_user_id: int,
                      ) -> None:
        """ try to init game """
        # каждый сезон карты местности перетасовываются, а после хода карта откладывается
        initial_cards = self._get_initial_cards()
        season_ids = SeasonDaoRedis(R).pre_init_seasons(initial_cards)
        room_id, player_ids = self._get_room_and_players(initiator_user_id)
        (room_dao := RoomDao(R)).check_user_is_admin(room_id,
                                                     initiator_user_id)
        room_dao.set_is_game_started(room_id, True)

        game_id = self._create_game_model(
            initial_cards=initial_cards,
            season_ids=season_ids,
            player_ids=player_ids,
            room_id=room_id,
            admin_id=initiator_user_id,
        ).id

        self._add_game_id_by_player_id_index_many(game_id, player_ids)

    def fetch_game_pretty(self,
                          user_id: int,
                          ) -> GamePretty:
        player_dao, move_dao = PlayerDao(R), MoveDao(R)


        player_id = player_dao.fetch_player_id_by_user_id(user_id)
        game_id = self._fetch_game_id_by_player_id(player_id)
        game: GameDC = self.fetch_dc_model(game_id)

        seasons_score_id = player_dao.get_seasons_score_id(player_id)
        seasons_score = SeasonsScoreDao(R).fetch_seasons_score_pretty(
            seasons_score_id
        )
        season_ids = self._fetch_season_ids(game_id)

        game_pretty = GamePretty(
            id=game_id,
            room_name=RoomDao(R).fetch_room_name(game.room_id),
            player_field=player_dao.fetch_field_pretty(player_id),
            seasons=(season_dao := SeasonDaoRedis(R)).get_seasons_pretty(
                season_ids
            ),
            # tasks=season_dao.get_tasks_pretty(game.season_ids),
            current_season_name=season_dao.fetch_season_name(
                game.current_season_id
            ),
            players=player_dao.get_players_pretty(game.player_ids),
            discovery_card=move_dao.fetch_discovery_card_pretty(
                season_dao.fetch_move_id(
                    self._fetch_current_season_id(game_id)
                )
            ),
            is_prev_card_ruins=move_dao.fetch_is_prev_card_ruins(
                season_dao.fetch_move_id(game.current_season_id)
            ),
            player_coins=player_dao.fetch_coins(player_id),
            player_score=self._extract_current_score(seasons_score),
            season_scores=seasons_score,

        )

        return game_pretty

    def process_move(self,
                     user_id: int,
                     updated_field: FieldPretty,
                     ) -> None:
        player_dao = PlayerDao(R)

        player_id = player_dao.fetch_player_id_by_user_id(user_id)
        player_dao.finish_move_for_player(
            player_id=player_id,
            updated_field=utils.decode_pretty_field(updated_field),
        )

        self._prepare_for_next_move(
            game_id := self._fetch_game_id_by_player_id(player_id)
        )

        if not self._check_game_finished(game_id):
            self._start_new_move(game_id)

    def try_kick_player(self,
                        kicker_id: int,
                        player_to_kick_id: int,
                        ) -> None:
        pass

    def try_leave(self,
                  player_id: int,
                  ) -> None:
        game_id = self._fetch_game_id_by_player_id(player_id)
        self._delete_player(game_id, player_id)

    def check_is_new_move_started(self,
                                  user_id: int,
                                  ) -> bool:

        player_ids = self._fetch_player_ids(
            game_id=self._fetch_game_id_by_user_id(user_id)
        )
        return PlayerDao(R).check_all_players_not_finished_move(player_ids)

    def _fetch_game_id_by_user_id(self,
                                  user_id: int,
                                  ) -> int:
        player_id = PlayerDao(R).fetch_player_id_by_user_id(user_id)
        return self._fetch_game_id_by_player_id(player_id)

    def _delete_player(self,
                       game_id: int,
                       player_id: int,
                       ) -> None:
        self._remove_player_id(game_id, player_id)
        self._delete_game_id_by_player_id_index(player_id)

    def _remove_player_id(self,
                          game_id: int,
                          player_id: int,
                          ) -> None:
        PlayerDao(R).remove_player_id_from_neighbors(player_id)
        self._remove_player_id_from_player_ids(game_id, player_id)

    def _remove_player_id_from_player_ids(self,
                                          game_id: int,
                                          player_id: int,
                                          ) -> None:
        player_ids = self._fetch_player_ids(game_id)
        player_ids.remove(player_id)
        self._set_player_ids(game_id, player_ids)

    def _set_player_ids(self,
                        game_id: int,
                        player_ids: MutableSequence[int],
                        ) -> None:
        self._set_model_attr(game_id, 'player_ids', player_ids)

    def _delete_game_id_by_player_id_index(self,
                                           player_id: int,
                                           ) -> None:
        key = self._key_schema.game_id_by_player_id_index_key
        self._redis.hdel(key, player_id)

    def _check_game_finished(self,
                             game_id: int,
                             ) -> bool:
        is_finished = self._fetch_model_attr(game_id, 'is_finished')
        return is_finished

    def _prepare_for_next_move(self,
                               game_id: int,
                               ) -> None:
        if self._check_all_players_finished_move(game_id):
            if self._check_season_points_exceeded(game_id):
                self._switch_to_next_season(game_id)
                if self._check_seasons_exceeded(game_id):
                    self._finish_game(game_id)

    def _check_season_points_exceeded(self,
                                      game_id: int,
                                      ) -> bool:
        current_season_id = self._fetch_current_season_id(game_id)
        points_exceeded = SeasonDaoRedis(R).check_season_points_exceeded(
            current_season_id
        )
        return points_exceeded

    def _finish_game(self,
                     game_id: int,
                     ) -> None:
        self._set_model_attr(game_id, 'is_finished', True)

    def _fetch_last_season_id(self,
                              game_id: int,
                              ) -> int:
        last_season_id = self._fetch_model_attr(game_id, 'last_season_id')
        services.utils.validate_not_none(last_season_id)

        return last_season_id

    # def _switch_to_next_season(self,
    #                            game_id: int,
    #                            ) -> None:
    #     current_season_id = self._fetch_current_season_id(game_id)
    #     next_season_id = self._fetch_next_season_id(game_id,
    #                                                 current_season_id)
    #
    #     season_dao = SeasonDaoRedis(REDIS)
    #     unused_monster_cards = season_dao.finish_season(current_season_id)
    #     season_dao.init_season(next_season_id, unused_monster_cards)
    #
    #     self._set_current_season_id(game_id, next_season_id)

    def _add_game_id_by_player_id_index_many(self,
                                             game_id: int,
                                             player_ids: Iterable[int],
                                             ) -> None:
        for player_id in player_ids:
            self._add_game_id_by_player_id_index(game_id, player_id)

    def _fetch_season_ids(self,
                          game_id: int,
                          ) -> list[int]:
        season_ids = self._fetch_model_attr(
            model_id=game_id,
            field_name='season_ids',
        )
        services.utils.validate_not_none(season_ids)

        return season_ids

    @staticmethod
    def _extract_current_score(seasons_score: SeasonsScorePretty,
                               ) -> int:
        spring_total = seasons_score['spring_score']['total']
        summer_total = seasons_score['summer_score']['total']
        fall_total = seasons_score['fall_score']['total']
        winter_total = seasons_score['winter_score']['total']

        return spring_total + summer_total + fall_total + winter_total

    def _fetch_game_id_by_player_id(self,
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

    def _start_new_move(self,
                        game_id: int,
                        ) -> None:

        SeasonDaoRedis(R).start_new_move(
            self._fetch_current_season_id(game_id)
        )
        self._set_players_move_not_finished(game_id)

    def _set_players_move_not_finished(self,
                                       game_id: int,
                                       ) -> None:
        player_ids = self._fetch_player_ids(game_id)
        PlayerDao(R).set_players_move_not_finished(player_ids)

    def _switch_to_next_season(self,
                               game_id: int,
                               ) -> None:
        season_dao = SeasonDaoRedis(R)

        unused_monster_card_ids = season_dao.fetch_monster_card_ids(
            self._fetch_current_season_id(game_id)
        )
        season_dao.finish_init_season(
            next_season_id := self._fetch_next_season_id(game_id),
            unused_monster_card_ids,
        )
        self._set_current_season_id(game_id, next_season_id)

    def _fetch_current_season_id(self,
                                 game_id: int,
                                 ) -> int:
        current_season_id = self._fetch_model_attr(game_id,
                                                   'current_season_id')
        services.utils.validate_not_none(current_season_id)

        return current_season_id

    def _set_current_season_id(self,
                               game_id: int,
                               season_id: int,
                               ) -> None:
        self._set_model_attr(game_id, 'current_season_id', season_id)

    def _fetch_next_season_id(self,
                              game_id: int,
                              ) -> int:
        season_ids = self._fetch_season_ids(game_id)
        current_season_id = self._fetch_current_season_id(game_id)
        next_season_id_index = season_ids.index(current_season_id) + 1
        next_season_id = season_ids[next_season_id_index]
        return next_season_id

    @staticmethod
    def _get_initial_cards():
        terrain_card_ids = TerrainCardDao(R).pick_terrain_cards()

        monster_card_ids = MonsterCardDaoRedis(R).pick_monster_cards()

        objective_card_ids = ObjectiveCardDaoRedis(R).pick_objective_cards()

        initial_cards = InitialCards(terrain_card_ids,
                                     monster_card_ids,
                                     objective_card_ids)

        return initial_cards

    def _check_seasons_exceeded(self,
                                game_id: int,
                                ) -> bool:
        """ Check if game has ended, but it's not indicated in system """
        last_season_id = self._fetch_last_season_id(game_id)
        return SeasonDaoRedis(R).check_season_finished(last_season_id)

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
            last_season_id=season_ids[3],
            is_finished=False,
        )
        self.insert_dc_model(game)
        self._add_game_id_by_room_id_index(room_id, game_id)

        return game

    def _check_all_players_finished_move(self,
                                         game_id: int,
                                         ) -> bool:
        player_ids = self._fetch_player_ids(game_id)
        return PlayerDao(R).check_players_finished_move(player_ids)

    def _fetch_player_ids(self,
                          game_id: int,
                          ) -> list[int]:
        player_ids = self._fetch_model_attr(game_id, 'player_ids')
        services.utils.validate_not_none(player_ids)

        return player_ids

    def _add_game_id_by_room_id_index(self,
                                      room_id: int,
                                      game_id: int,
                                      ) -> None:
        key = self._key_schema.game_id_by_room_id_index_key
        self._redis.hset(key, room_id, game_id)

    def _get_room_and_players(self,
                              admin_id: int,
                              ) -> tuple[int, list[int]]:
        user_ids = (room_dao := RoomDao(R)).fetch_user_ids(admin_id)
        field = self._gen_game_field()
        player_ids = PlayerDao(R).init_players(user_ids, field)
        room_id = room_dao._fetch_room_id_by_user_id(admin_id)

        return room_id, player_ids

    def _add_game_id_by_player_id_index(self,
                                        game_id: int,
                                        player_id: int,
                                        ) -> None:
        key = self._key_schema.game_id_by_player_id_index_key
        self._redis.hset(key, player_id, game_id)

    def _gen_game_field(self) -> Field:
        field = BLANK_FIELD
        return field


class ObjectiveCardDaoRedis(DaoFull):
    OBJECTIVE_CARD_QUANTITY = 4

    _key_schema = ObjectiveCardKeySchema()
    _converter = ObjectiveCardConverter()
    _model_class = ObjectiveCardDC

    def pick_objective_cards(self) -> list[int]:  # it's copypasta!
        card_ids_key = self._key_schema.ids_key
        card_ids = [int(id) for id in self._redis.smembers(card_ids_key)]

        picked_card_ids = random.sample(card_ids,
                                        self.OBJECTIVE_CARD_QUANTITY)
        return picked_card_ids


class TerrainCardDao(DiscoveryCardDao):
    TERRAIN_CARD_QUANTITY = 2

    _key_schema = TerrainCardKeySchema()
    _converter = TerrainCardConverter()
    _model_class = TerrainCardDC

    def fetch_terrain_pretty(self,
                             terrain_card_id: int,
                             ) -> int:
        terrain = self._fetch_model_attr(
            model_id=terrain_card_id,
            field_name='terrain',
            converter=services.utils.decode_bytes
        )
        services.utils.validate_not_none(terrain)

        terrain_pretty = TERRAIN_STR_TO_NUM[terrain]
        return terrain_pretty

    def fetch_additional_terrain_pretty(self,
                                        terrain_card_id: int,
                                        ) -> Optional[int]:
        additional_terrain = self._fetch_model_attr(
            model_id=terrain_card_id,
            field_name='additional_terrain',
            converter=services.utils.decode_bytes,
        )
        # if no add_terrain, then return None
        additional_terrain_pretty = (additional_terrain
                                     and TERRAIN_STR_TO_NUM[additional_terrain])
        return additional_terrain_pretty

    def fetch_additional_shape_pretty(self,
                                      terrain_card_id: int,
                                      ) -> Optional[ShapePretty]:
        additional_shape_id = self._fetch_model_attr(
            model_id=terrain_card_id,
            field_name='additional_shape_id',
            converter=services.utils.deserialize,
        )
        if additional_shape_id is None:
            return None

        additional_shape_dc: ShapeDC = ShapeDaoRedis(R).fetch_dc_model(
            additional_shape_id
        )
        additional_shape_pretty = ShapePretty(
            shape_value=additional_shape_dc.shape_value,
            gives_coin=additional_shape_dc.gives_coin,
        )
        return additional_shape_pretty

    def pick_terrain_cards(self):
        card_ids_key = self._key_schema.ids_key
        card_ids = [int(id) for id in self._redis.smembers(card_ids_key)]

        picked_card_ids = random.sample(card_ids,
                                        self.TERRAIN_CARD_QUANTITY)
        return picked_card_ids

    def pick_terrain_card_id(self,
                             card_ids: MutableSequence[int],
                             allow_ruins: bool,
                             ) -> int:
        while True:
            card_id = self._pick_card_id(card_ids)
            if allow_ruins or not self.check_card_is_ruins(card_id):
                card_ids.remove(card_id)
                return card_id

    def fetch_card_type(self,
                        terrain_card_id: int,
                        ) -> str:
        card_type = self._fetch_model_attr(terrain_card_id, 'card_type',
                                           services.utils.decode_bytes)
        services.utils.validate_not_none(card_type)

        return card_type

    def fetch_regular_card_season_points(self,
                                         card_id: int,
                                         ) -> int:
        points = self._fetch_model_attr(card_id, 'season_points')
        services.utils.validate_not_none(points)

        return points

    def check_card_is_ruins(self,
                            card_id: int,
                            ) -> bool:
        return TerrainCardDao(R).check_terrain_card_type(card_id, 'ruins')

    def check_card_is_anomaly(self,
                              card_id: int,
                              ) -> bool:
        return TerrainCardDao(R).check_terrain_card_type(card_id, 'anomaly')

    def check_terrain_card_type(self,
                                card_id: int,
                                checked_card_type: str,
                                ) -> bool:
        actual_card_type = self.fetch_card_type(card_id)
        return actual_card_type == checked_card_type


class ShapeDaoRedis(DaoFull):
    _key_schema = ShapeKeySchema()
    _converter = ShapeConverter()
    _model_class = ShapeDC


class SeasonDaoRedis(DaoRedis):
    _key_schema = SeasonKeySchema()
    _converter = SeasonConverter()
    _model_class = SeasonDC

    def fetch_move_id(self,
                      season_id: int,
                      ) -> int:
        move_id = self._fetch_model_attr(season_id, 'current_move_id')
        services.utils.validate_not_none(move_id)

        return move_id

    def check_season_finished(self,
                              season_id: int,
                              ) -> bool:
        is_finished = self._fetch_model_attr(season_id, 'is_finished')
        services.utils.validate_not_none(is_finished)

        return is_finished

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

    def pre_init_seasons(self,
                         initial_cards: InitialCards,
                         ) -> list[int]:
        print(initial_cards)
        """ create seasons, insert them into redis
         and return their ids """

        objective_card_ids = initial_cards.objective_card_ids
        terrain_card_ids = initial_cards.terrain_card_ids
        monster_card_ids = initial_cards.monster_card_ids

        season_cards = self._get_season_cards()

        seasons = []
        seasons.append(self.pre_init_season(
            name=ESeasonName.SPRING,
            season_card=season_cards.spring,
            objective_card_ids=objective_card_ids[0:2],
            terrain_card_ids=self._shuffle_cards(terrain_card_ids),
            monster_card_ids=[monster_card_ids.pop()],
            is_first_season=True,
        ))
        seasons.append(self.pre_init_season(
            name=ESeasonName.SUMMER,
            season_card=season_cards.summer,
            objective_card_ids=objective_card_ids[1:3],
            terrain_card_ids=self._shuffle_cards(terrain_card_ids),
            monster_card_ids=[monster_card_ids.pop()],
            is_first_season=False,
        ))
        seasons.append(self.pre_init_season(
            name=ESeasonName.FALL,
            season_card=season_cards.fall,
            objective_card_ids=objective_card_ids[2:4],
            terrain_card_ids=self._shuffle_cards(terrain_card_ids),
            monster_card_ids=[monster_card_ids.pop()],
            is_first_season=False,
        ))
        seasons.append(self.pre_init_season(
            name=ESeasonName.WINTER,
            season_card=season_cards.winter,
            objective_card_ids=[objective_card_ids[0],
                                objective_card_ids[3]],
            terrain_card_ids=self._shuffle_cards(objective_card_ids),
            monster_card_ids=[monster_card_ids.pop()],
            is_first_season=False,
        ))

        return seasons

    def pre_init_season(self,
                        name: ESeasonName,
                        season_card: SeasonCardSQL,
                        objective_card_ids: MutableSequence[int],
                        terrain_card_ids: MutableSequence[int],
                        monster_card_ids: MutableSequence[int],
                        is_first_season: bool,
                        ) -> int:
        """
        Create season (not complete monster cards),
        insert it and return its id.
        If first season, then it can't be ruins.
        """
        first_move_id = self.start_new_move(
            terrain_card_ids=terrain_card_ids,
            monster_card_ids=monster_card_ids,
            is_on_ruins_allowed=False,
        ) if is_first_season else None

        season = self._model_class(
            id=self._gen_new_id(),
            name=name,
            image_url=season_card.image.url,
            current_points=0,
            max_points=season_card.points_to_end,
            objective_card_ids=objective_card_ids,
            terrain_card_ids=terrain_card_ids,
            monster_card_ids=monster_card_ids,
            current_move_id=first_move_id,
            is_finished=False,
        )
        self.insert_dc_model(season)

        return season.id

    def finish_init_season(self,
                           season_id: int,
                           unused_monster_card_ids: Iterable[int],
                           ) -> None:
        self._add_monster_card_ids(season_id, unused_monster_card_ids)

    def _set_current_move_id(self,
                             season_id: int,
                             move_id: int,
                             ) -> None:
        self._set_model_attr(season_id, 'current_move_id', move_id)

    def _add_monster_card_ids(self,
                              season_id: int,
                              unused_monster_card_ids: Iterable[int],
                              ) -> None:
        current_monster_card_ids = self._fetch_monster_card_ids(season_id)
        current_monster_card_ids.extend(unused_monster_card_ids)
        self._set_monster_card_ids(season_id, current_monster_card_ids)

    def _set_monster_card_ids(self,
                              season_id: int,
                              monster_card_ids: MutableSequence[int],
                              ):
        self._set_model_attr(season_id, 'monster_card_ids', monster_card_ids)

    def _fetch_monster_card_ids(self,
                                season_id: int,
                                ) -> list[int]:
        monster_card_ids = self._fetch_model_attr(season_id,
                                                  'monster_card_ids')
        services.utils.validate_not_none(monster_card_ids)

        return monster_card_ids

    def get_seasons_pretty(self,
                           season_ids: Iterable[int],
                           ) -> dict[SeasonName: SeasonPretty]:
        seasons = {
            (season := self.fetch_season_pretty(season_id)).name: season.url
            for season_id in season_ids
        }
        services.utils.validate_not_none(seasons)

        return seasons

    def fetch_season_pretty(self,
                            season_id: int,
                            ) -> SeasonPretty:
        name = self.fetch_season_name(season_id)
        url = self.fetch_image_url(season_id)
        return SeasonPretty(name, url)

    def fetch_image_url(self,
                        season_id: int,
                        ) -> str:
        url = self._fetch_model_attr(season_id,
                                     'image_url',
                                     services.utils.decode_bytes)
        services.utils.validate_not_none(url)

        return url

    def check_season_points_exceeded(self,
                                     season_id: int,
                                     ) -> bool:
        max_points = self._fetch_max_points(season_id)
        current_points = self._fetch_current_points(season_id)
        return current_points >= max_points

    def finish_season(self,
                      season_id: int,
                      ) -> list[int]:
        self._set_is_finished(season_id, True)
        unused_monster_card_ids = self.fetch_monster_card_ids(season_id)
        return unused_monster_card_ids

    def _set_is_finished(self,
                         season_id: int,
                         value: bool,
                         ) -> None:
        self._set_model_attr(season_id, 'is_finished', value)

    def fetch_season_name(self,
                          season_id: int,
                          ) -> str:
        season_name = self._fetch_model_attr(
            model_id=season_id,
            field_name='name',
            converter=services.utils.decode_bytes,
        )
        services.utils.validate_not_none(season_name)

        return season_name

    def _fetch_max_points(self,
                          season_id: int,
                          ) -> int:
        points = self._fetch_model_attr(season_id, 'max_points')
        services.utils.validate_not_none(points)

        return points

    def _fetch_current_points(self,
                              season_id: int,
                              ) -> int:
        points = self._fetch_model_attr(season_id, 'current_points')
        services.utils.validate_not_none(points)

        return points

    @staticmethod
    def _get_season_cards() -> SeasonCards:
        cards = SeasonCards(
            spring=SeasonCardSQL.objects.get(name__iexact='весна'),
            summer=SeasonCardSQL.objects.get(name__iexact='лето'),
            fall=SeasonCardSQL.objects.get(name__iexact='осень'),
            winter=SeasonCardSQL.objects.get(name__iexact='зима'),
        )
        return cards

    def start_new_move(self,
                       season_id: int | None = None,
                       terrain_card_ids: MutableSequence[int] | None = None,
                       monster_card_ids: MutableSequence[int] | None = None,
                       is_on_ruins_allowed: bool | None = None,
                       ) -> int:
        """ Requires: either season_id or cards.
        When starting new move, we need to consider if it's on ruins """
        # if ruins allowed, then it must be skipped and considered for next move.
        (card_id,
         card_type,
         is_on_ruins) = DiscoveryCardDao(R).pick_card_and_is_on_ruins(
            terrain_card_ids or self._fetch_terrain_card_ids(season_id),
            monster_card_ids or self._fetch_monster_card_ids(season_id),
            is_on_ruins_allowed,
        )
        print('-' * 20, ':', card_id, card_type, is_on_ruins)

        season_id and self._add_card_season_points(season_id)
        new_move_id = MoveDao(R).init_move(
            discovery_card_id=card_id,
            discovery_card_type=card_type,
            is_on_ruins=is_on_ruins,
        )
        season_id and self._set_current_move_id(season_id, new_move_id)

        return new_move_id

    def _add_card_season_points(self,
                                season_id: int,
                                ) -> None:
        current_points = self._fetch_current_points(season_id)
        move_id = self._fetch_current_move_id(season_id)
        self._set_current_points(
            season_id,
            current_points + MoveDao(R).fetch_card_season_points(
                move_id
            ),
        )

    def _set_current_points(self,
                            season_id: int,
                            value: int,
                            ) -> None:
        self._set_model_attr(season_id, 'current_points', value)

    def _fetch_terrain_card_ids(self,
                                season_id: int,
                                ) -> list[int]:
        card_ids = self._fetch_model_attr(season_id, 'terrain_card_ids')
        services.utils.validate_not_none(card_ids)

        return card_ids

    def fetch_monster_card_ids(self,
                               season_id: int,
                               ) -> list[int]:
        card_ids = self._fetch_model_attr(season_id, 'monster_card_ids')
        services.utils.validate_not_none(card_ids)

        return card_ids

    def _check_card_is_ruins(self,
                             season_id: int,
                             ) -> bool:
        current_move_id = self._fetch_current_move_id(season_id)
        if current_move_id is None:
            return False

        return MoveDao(R).check_card_is_ruins(current_move_id)

    def _fetch_current_move_id(self,
                               season_id: int,
                               ) -> int:
        move_id = self._fetch_model_attr(season_id, 'current_move_id')
        services.utils.validate_not_none(move_id)

        return move_id

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


class MoveDao(DaoRedis):
    _key_schema = MoveKeySchema()
    _converter = MoveConverter()
    _model_class = MoveDC

    def init_move(self,
                  discovery_card_id: int,
                  discovery_card_type: EDiscoveryCardType,
                  is_on_ruins: bool,
                  ) -> int:
        move = self._model_class(
            id=self._gen_new_id(),
            is_on_ruins=is_on_ruins,
            discovery_card_id=discovery_card_id,
            discovery_card_type=discovery_card_type,
        )
        self.insert_dc_model(move)
        return move.id

    def fetch_is_prev_card_ruins(self,
                                 move_id: int,
                                 ) -> bool:
        is_prev_card_ruins = self._fetch_model_attr(
            model_id=move_id,
            field_name='is_on_ruins',
        )
        services.utils.validate_not_none(is_prev_card_ruins)

        return is_prev_card_ruins

    def fetch_card_season_points(self,
                                 move_id: int,
                                 ) -> int:
        if not self._check_card_is_terrain(move_id):
            return 0

        return self._fetch_terrain_card_season_points(move_id)

    def fetch_discovery_card_pretty(self,
                                    move_id: int,
                                    ) -> DiscoveryCardPretty:
        discovery_card_pretty = DiscoveryCardPretty(
            image=self._fetch_card_image_url(move_id),
            is_anomaly=self._check_card_is_anomaly(move_id),
            terrain_int=self._fetch_card_terrain_pretty(move_id),
            additional_terrain_int=self._fetch_card_additional_terrain(move_id),
            shape=self._fetch_card_shape_pretty(move_id),
            additional_shape=self._fetch_card_additional_shape_pretty(move_id),
        )
        return discovery_card_pretty

    def _fetch_terrain_card_season_points(self,
                                          move_id: int,
                                          ) -> int:
        match self._fetch_terrain_card_type(move_id):
            case 'regular':
                return self._fetch_regular_card_season_points(move_id)
            case 'anomaly', 'ruins':
                return 0

    def _fetch_regular_card_season_points(self,
                                          move_id: int,
                                          ) -> int:
        card_id = self._fetch_discovery_card_id(move_id)
        return TerrainCardDao(R).fetch_regular_card_season_points(card_id)

    def _fetch_terrain_card_type(self,
                                 move_id: int,
                                 ) -> str:
        card_id = self._fetch_discovery_card_id(move_id)
        services.utils.validate_not_none(card_id)

        return TerrainCardDao(R).fetch_card_type(card_id)

    def _check_card_is_anomaly(self,
                               move_id: int,
                               ) -> bool:
        if not self._check_card_is_terrain(move_id):
            return False

        return TerrainCardDao(R).check_card_is_anomaly(
            self._fetch_discovery_card_id(move_id)
        )

    def check_card_is_ruins(self,
                            move_id: int,
                            ) -> bool:
        # should I write this method in TerrainCardDao???
        if not self._check_card_is_terrain(move_id):
            return False

        return TerrainCardDao(R).check_card_is_ruins(
            self._fetch_discovery_card_id(move_id)
        )

    def _check_card_is_terrain(self,
                               move_id: int,
                               ) -> bool:
        discovery_card_type = self._fetch_discovery_card_type(move_id)
        if discovery_card_type != 'terrain':
            return False

    def _fetch_card_terrain_pretty(self,
                                   move_id: int,
                                   ) -> int:
        card_type = self._fetch_discovery_card_type(move_id)
        match card_type:
            case 'terrain':
                terrain = TerrainCardDao(R).fetch_terrain_pretty(
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

        terrain = TerrainCardDao(R).fetch_additional_terrain_pretty(
            terrain_card_id=self._fetch_discovery_card_id(move_id)
        )
        return terrain

    def _fetch_discovery_card_id(self,
                                 move_id: int,
                                 ) -> int:
        card_id = self._fetch_model_attr(
            model_id=move_id,
            field_name='discovery_card_id',
        )
        services.utils.validate_not_none(card_id)

        return card_id

    def _fetch_card_shape_pretty(self,
                                 move_id: int,
                                 ) -> ShapePretty:
        card_type = self._fetch_discovery_card_type(move_id)
        card_id = self._fetch_discovery_card_id(move_id)

        match card_type:
            case 'terrain':
                card_dao = TerrainCardDao(R)
            case 'monster':
                card_dao = MonsterCardDaoRedis(R)
            case _:
                raise ValueError('type must be either "monster" or "terrain"')

        shape = card_dao.fetch_shape_pretty(card_id)

        return shape

    def _fetch_card_additional_shape_pretty(self,
                                            move_id: int,
                                            ) -> Optional[str]:
        card_id = self._fetch_discovery_card_id(move_id)
        if not self._check_card_is_terrain(move_id):
            return None

        return TerrainCardDao(R).fetch_additional_shape_pretty(
            card_id
        )

    def _fetch_is_prev_card_ruins(self,
                                  move_id: int,
                                  ) -> bool:
        is_prev_card_ruins = self._fetch_model_attr(
            model_id=move_id,
            field_name='is_prev_card_ruins',
        )
        services.utils.validate_not_none(is_prev_card_ruins)

        return is_prev_card_ruins

    def _fetch_card_image_url(self,
                              move_id: int,
                              ) -> URL:
        card_type = self._fetch_discovery_card_type(move_id)

        match card_type:  # why not use Literal for card_type everywhere
            case 'terrain':
                discovery_card_dao = TerrainCardDao(R)
            case 'monster':
                discovery_card_dao = MonsterCardDaoRedis(R)
            case _:
                raise ValueError('Type of discovery card must be either '
                                 '"terrain" or "monster"')

        url = discovery_card_dao.fetch_image_url(
            self._fetch_discovery_card_id(move_id)
        )

        return url

    def _fetch_discovery_card_type(self,
                                   move_id: int,
                                   ) -> str:
        # print(move_id)
        card_type = self._fetch_model_attr(
            model_id=move_id,
            field_name='discovery_card_type',
            converter=services.utils.decode_bytes,
        )
        services.utils.validate_not_none(card_type)

        return card_type


# TODO: it will be nice to use deck-type structure for cards in the future
class PlayerDao(DaoRedis):
    _key_schema = PlayerKeySchema()
    _converter = PlayerConverter()
    _model_class = PlayerDC

    def get_players_pretty(self,
                           player_ids: Iterable[int],
                           ) -> list[PlayerPretty]:
        players = [
            self._get_player_pretty(player_id)
            for player_id in player_ids
        ]
        return players

    def set_players_move_not_finished(self,
                                      player_ids: Iterable[int],
                                      ) -> None:
        for player_id in player_ids:
            self._set_is_move_finished(player_id, True)

    def check_all_players_not_finished_move(self,
                                            player_ids: MutableSequence[int],
                                            ) -> bool:
        """ affectively checks if new move started
         if called after at least one player finished move """
        return all(
            not self._fetch_is_move_finished(player_id)
            for player_id in player_ids
        )

    def finish_move_for_player(self,
                               player_id: int,
                               updated_field: Field):
        self._set_field(player_id, updated_field)
        self._set_is_move_finished(player_id, True)

    def check_players_finished_move(self,
                                    player_ids: Iterable[int],
                                    ) -> bool:
        return all(
            self._fetch_is_move_finished(player_id)
            for player_id in player_ids
        )

    def remove_player_id_from_neighbors(self,
                                        player_id: int,
                                        ) -> None:
        player_dao = PlayerDao(R)

        player: PlayerDC = player_dao.fetch_dc_model(player_id)
        left_player: PlayerDC
        right_player: PlayerDC
        left_player, right_player = player_dao.fetch_dc_models(
            (left_player := player.left_player_id,
             right_player := player.right_player_id)
        )

        left_player.right_player_id = right_player.id
        right_player.left_player_id = left_player.id

        self.insert_dc_models((left_player, right_player))

    def _fetch_is_move_finished(self,
                                player_id,
                                ) -> bool:
        is_move_finished = self._fetch_model_attr(player_id, 'is_move_finished')
        services.utils.validate_not_none(is_move_finished)

        return is_move_finished

    def _set_field(self,
                   player_id: int,
                   updated_field: Field,
                   ) -> None:
        self._set_model_attr(
            model_id=player_id,
            field_name='field',
            value=updated_field,
            converter=utils.serialize_field,
        )

    def _set_is_move_finished(self,
                              player_id: int,
                              value: bool,
                              ) -> None:
        self._set_model_attr(player_id, 'finished_move', value)

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
        id = self._fetch_model_attr(
            model_id=player_id,
            field_name='seasons_score_id',
            converter=int,
        )
        return id

    def fetch_player_id_by_user_id(self,
                                   user_id: int,
                                   ) -> int:
        key = self._key_schema.player_id_by_user_id_index_key
        player_id = int(self._redis.hget(key, user_id))
        return player_id

    def fetch_field_pretty(self,
                           player_id: int,
                           ) -> list[list[int]]:
        field_pretty = self._fetch_model_attr(
            model_id=player_id,
            field_name='field',
            converter=lambda x: self._make_field_pretty(
                games.utils.deserialize_field(x)
            ),
        )
        services.utils.validate_not_none(field_pretty)

        return field_pretty

    def fetch_coins(self,
                    player_id: int,
                    ) -> int:
        coins = self._fetch_model_attr(player_id, 'coins')
        services.utils.validate_not_none(coins)

        return coins

    def get_score_total(self,
                        player_id: int,
                        ) -> int:
        seasons_score_id = self._fetch_seasons_score_id(player_id)
        total = SeasonsScoreDao(R).fetch_score(seasons_score_id)

        return total

    def fetch_name(self,
                   player_id: int,
                   ) -> str:
        user_id = self._fetch_user_id(player_id)
        name = User.objects.get(pk=user_id).username

        return name

    def _fetch_seasons_score_id(self,
                                player_id: int,
                                ) -> int:
        seasons_score_id = self._fetch_model_attr(
            model_id=player_id,
            field_name='seasons_score_id',
        )
        services.utils.validate_not_none(seasons_score_id)

        return seasons_score_id

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
        seasons_score_id = SeasonsScoreDao(R).init_seasons_score()  # create seasons for players
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
            is_move_finished=False,
        )
        return player_dc

    def _get_player_pretty(self,
                           player_id: int,
                           ) -> PlayerPretty:
        return PlayerPretty(
            id=player_id,
            name=self.fetch_name(player_id),
            score=self.get_score_total(player_id)
        )

    @staticmethod
    def _make_field_pretty(field: Field,
                           ) -> FieldPretty:
        field_pretty = [
            [TERRAIN_STR_TO_NUM[cell.value] for cell in row]
            for row in field
        ]
        return field_pretty

    def _fetch_user_id(self,
                       player_id: int,
                       ) -> int:
        user_id = self._fetch_model_attr(
            model_id=player_id,
            field_name='user_id',
        )
        services.utils.validate_not_none(user_id)

        return user_id


class SeasonsScoreDao(DaoRedis):
    _key_schema = SeasonsScoreKeySchema()
    _converter = SeasonsScoreConverter()
    _model_class = SeasonsScoreDC

    def init_seasons_score(self) -> int:
        season_score_dao = SeasonScoreDao(R)
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

    def fetch_seasons_score_pretty(self,
                                   seasons_score_id: int,
                                   ) -> SeasonsScorePretty:
        ids = self._fetch_season_score_ids(seasons_score_id)
        dao = SeasonScoreDao(R)

        seasons_score = SeasonsScorePretty(
            spring_score=dao.fetch_season_score_pretty(ids[0]),
            summer_score=dao.fetch_season_score_pretty(ids[1]),
            fall_score=dao.fetch_season_score_pretty(ids[2]),
            winter_score=dao.fetch_season_score_pretty(ids[3]),
        )
        return seasons_score

    def fetch_score(self,
                    seasons_score_id: int,
                    ) -> int:
        season_score_ids = self._fetch_season_score_ids(seasons_score_id)
        total = SeasonScoreDao(R).fetch_seasons_score_total(season_score_ids)
        return total

    def _fetch_season_score_ids(self,
                                seasons_score_id: int,
                                ) -> list[int]:
        season_score_ids = [
            self._fetch_season_score_id(seasons_score_id,
                                        ESeasonName.SPRING),
            self._fetch_season_score_id(seasons_score_id,
                                        ESeasonName.SUMMER),
            self._fetch_season_score_id(seasons_score_id,
                                        ESeasonName.FALL),
            self._fetch_season_score_id(seasons_score_id,
                                        ESeasonName.WINTER),
        ]
        if len(season_score_ids) < 4:
            raise ValueError('must be 4 season score ids')

        return season_score_ids

    def _fetch_total(self,
                     seasons_score_id: int,
                     ) -> int:
        total = self._fetch_model_attr(
            model_id=seasons_score_id,
            field_name='total',
        )
        services.utils.validate_not_none(total)

        return total

    def _fetch_coins(self,
                     seasons_score_id: int,
                     ) -> int:
        coins = self._fetch_model_attr(
            model_id=seasons_score_id,
            field_name='coins',
        )
        services.utils.validate_not_none(coins)

        return coins

    def _fetch_season_score_id(self,
                               seasons_score_id: int,
                               season: ESeasonName):
        season_score_id = self._fetch_model_attr(
            model_id=seasons_score_id,
            field_name=f'{season.value}_score_id',
        )
        services.utils.validate_not_none(season_score_id)

        return season_score_id


class SeasonScoreDao(DaoRedis):
    _key_schema = SeasonScoreKeySchema()
    _converter = SeasonScoreConverter()
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

    def fetch_seasons_score_total(self,
                                  season_score_ids: Iterable[int],
                                  ) -> int:
        total = sum(
            self._fetch_season_score_total(season_score_id)
            for season_score_id in season_score_ids
        )
        return total

    def fetch_season_score_pretty(self,
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

    def _fetch_season_score_total(self,
                                  season_score_id: int,
                                  ) -> int:
        total = self._fetch_model_attr(
            model_id=season_score_id,
            field_name='total',
        )
        services.utils.validate_not_none(total)

        return total


class MonsterCardDaoRedis(DiscoveryCardDao):
    _key_schema = MonsterCardKeySchema()
    _converter = MonsterCardConverter()
    MONSTER_CARD_QUANTITY = 4

    def pick_monster_cards(self,
                           ) -> list[int]:
        card_ids_key = self._key_schema.ids_key
        card_ids = [int(id) for id in self._redis.smembers(card_ids_key)]

        picked_card_ids = random.sample(card_ids,
                                        self.MONSTER_CARD_QUANTITY)
        return picked_card_ids
