import random
from copy import copy
from typing import MutableSequence, NamedTuple, Iterable, Optional, TypeAlias, Sequence, overload, Literal, Any

from django.contrib.auth.models import User

import services.utils
import services.common
from cartographers_back.settings import R
from rooms.redis.dao import RoomDao
from services.redis.base.redis_dao_base import DaoRedis, DaoFull
from .dict_models import GamePretty, PlayerPretty, SeasonName, URL, DiscoveryCardPretty, \
    SeasonsScorePretty, SpringScorePretty, SummerScorePretty, FallScorePretty, WinterScorePretty, ShapePretty, \
    SeasonScorePretty, ObjectiveCardPretty, GameResultsPretty, PlayerResultPretty, ObjectiveCardsByCategory
from .key_schemas import MonsterCardKeySchema, GameKeySchema, SeasonKeySchema, MoveKeySchema, PlayerKeySchema, \
    TerrainCardKeySchema, ObjectiveCardKeySchema, SeasonsScoreKeySchema, SeasonScoreKeySchema, ShapeKeySchema
from .converters import MonsterCardConverter, GameConverter, SeasonConverter, MoveConverter, \
    TerrainCardConverter, ObjectiveCardConverter, PlayerConverter, SeasonsScoreConverter, \
    SeasonScoreConverter, ShapeConverter
from .dc_models import SeasonDC, GameDC, MoveDC, TerrainCardDC, ESeasonName, EDiscoveryCardType, \
    ObjectiveCardDC, PlayerDC, SeasonsScoreDC, SeasonScoreDC, ShapeDC
from .. import utils
from ..common import ETerrainTypeAll, TERRAIN_STR_TO_NUM, FieldPretty, FieldRegular, BLANK_FIELD, EExchangeOrder, \
    EObjectiveCardCategory
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
    clockwise_player_id: int
    player_id: int
    counterclockwise_player_id: int


class DiscoveryCardDao(DaoFull):

    def fetch_shape_pretty(self,
                           discovery_card_id: int,
                           ) -> ShapePretty | None:
        shape_id = self._fetch_model_attr(
            model_id=discovery_card_id,
            field_name='shape_id',
            converter=int,
        )
        if shape_id is None:
            return None

        shape_dc: ShapeDC = ShapeDaoRedis(R).fetch_dc_model(shape_id)
        shape_pretty = ShapePretty(
            shape_value=shape_dc.shape_value,
            gives_coin=shape_dc.gives_coin,
        )
        return shape_pretty

    def check_card_is_ruins(self,
                            card_id: int,
                            discovery_card_type: EDiscoveryCardType,
                            ) -> bool:
        if discovery_card_type is not EDiscoveryCardType.TERRAIN:
            return False

        return TerrainCardDao(R).check_card_is_ruins(card_id)

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
        # TODO: переименовать is_ruins_allowed во что-то вроде "отложить руины, если выпадут и прокручивать дальше"

        card_type = self._pick_card_type(
            terrain_cards_quantity=len(terrain_card_ids),
            monster_cards_quantity=len(monster_card_ids),
        )

        if card_type is EDiscoveryCardType.MONSTER:
            card_id = self._pick_card_id(monster_card_ids)
        elif card_type is EDiscoveryCardType.TERRAIN:
            card_id = TerrainCardDao(R).pick_card_id(
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
        services.utils.validate_not_none(is_on_ruins_allowed)

        is_on_ruins = False
        card_id, discovery_card_type = self.pick_card(
            terrain_card_ids=terrain_card_ids,
            monster_card_ids=monster_card_ids,
            is_ruins_allowed=is_on_ruins_allowed,
        )

        if is_on_ruins_allowed and DiscoveryCardDao(R).check_card_is_ruins(
                card_id, discovery_card_type,
        ):
            is_on_ruins = True
            card_id, discovery_card_type = self.pick_card(
                terrain_card_ids=terrain_card_ids,
                monster_card_ids=monster_card_ids,
                is_ruins_allowed=False,
            )

        return card_id, discovery_card_type, is_on_ruins

    @staticmethod
    def _pick_card_type(terrain_cards_quantity: int,
                        monster_cards_quantity: int,
                        ) -> EDiscoveryCardType:

        random_type = random.choices(
            population=(EDiscoveryCardType.TERRAIN,
                        EDiscoveryCardType.MONSTER),
            weights=(terrain_cards_quantity,
                     monster_cards_quantity),
        )[0]

        return random_type


class GameDao(DaoRedis):
    MONSTER_CARDS_AMOUNT = 4
    SEASONS_IN_GAME = 4

    _key_schema = GameKeySchema()
    _converter = GameConverter()

    def init_game(self,
                  initiator_user_id: int,
                  ) -> None:
        # каждый сезон карты местности перетасовываются, а после хода карта откладывается
        initial_cards = self._get_initial_cards()
        season_ids = SeasonDao(R).pre_init_seasons(initial_cards)
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

        seasons_score_id = player_dao.fetch_seasons_score_id(player_id)
        seasons_score = SeasonsScoreDao(R).fetch_seasons_score_pretty(
            seasons_score_id
        )
        season_ids = self._fetch_season_ids(game_id)

        game_pretty = GamePretty(
            id=game_id,
            room_name=RoomDao(R).fetch_room_name(game.room_id),
            player_field=self._fetch_field_pretty(game_id, player_id),
            seasons=(season_dao := SeasonDao(R)).get_seasons_pretty(
                season_ids
            ),
            tasks=season_dao.fetch_objective_cards_pretty(game.season_ids),
            current_season_name=season_dao.fetch_season_name(
                game.current_season_id
            ),
            players=player_dao.fetch_players_pretty(game.player_ids),
            discovery_card=move_dao.fetch_discovery_card_pretty(
                season_dao.fetch_move_id(
                    self._fetch_current_season_id(game_id)
                )
            ),
            is_on_ruins=move_dao.fetch_is_on_ruins(
                season_dao.fetch_move_id(game.current_season_id)
            ),
            player_coins=player_dao.fetch_coins(player_id),
            player_score=self._extract_current_score(seasons_score),
            season_scores=seasons_score,

        )

        return game_pretty

    def fetch_game_results(self,
                           user_id: int,
                           ) -> GameResultsPretty:
        game_id = self._fetch_game_id_by_user_id(user_id)
        game_results = GameResultsPretty(
            tasks=self._fetch_objective_cards_pretty(game_id),
            player_results=self._fetch_player_results_pretty(game_id),
        )
        return game_results

    def _fetch_objective_cards_pretty(self,
                                      game_id: int,
                                      ) -> list[ObjectiveCardPretty]:
        season_ids = self._fetch_season_ids(game_id)
        return SeasonDao(R).fetch_objective_cards_pretty(season_ids)

    def _fetch_player_results_pretty(self,
                                     game_id: int,
                                     ) -> list[PlayerResultPretty]:
        player_ids = self._fetch_player_ids(game_id)
        return PlayerDao(R).fetch_player_results_pretty(player_ids)

    def process_move(self,
                     user_id: int,
                     updated_field: FieldPretty,
                     ) -> None:
        player_id = PlayerDao(R).fetch_player_id_by_user_id(user_id)
        game_id = self._fetch_game_id_by_player_id(player_id)

        self._finish_move_for_player(
            game_id, player_id,
            games.utils.field_pretty_to_regular(updated_field),
        )

        if self._check_all_players_finished_move(game_id):
            self._prepare_for_next_move(game_id)
            if not self.check_game_is_finished(game_id=game_id):
                self._start_new_move(game_id)

    def try_kick_player(self,
                        kicker_id: int,
                        player_to_kick_id: int,
                        ) -> None:
        pass

    def leave(self,
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

    def _finish_move_for_player(self,
                                game_id: int,
                                player_id: int,
                                updated_field: FieldRegular,
                                ) -> None:
        if self._check_discovery_card_is_monster(game_id):
            PlayerDao(R).finish_move_for_player(
                player_id=player_id,
                updated_field=updated_field,
                exchange_order=self._fetch_exchange_order(game_id),
            )
        else:
            PlayerDao(R).finish_move_for_player(
                player_id=player_id,
                updated_field=updated_field,
                exchange_order=None,
            )

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

    def _fetch_field_pretty(self,
                            game_id: int,
                            player_id: int,
                            ) -> FieldPretty:
        if self._check_discovery_card_is_monster(game_id):
            return PlayerDao(R).fetch_neighbor_field_pretty(
                player_id,
                self._fetch_exchange_order(game_id),
            )

        return PlayerDao(R).fetch_field_pretty(player_id)

    def _fetch_exchange_order(self,
                              game_id: int,
                              ) -> EExchangeOrder:
        season_id = self._fetch_current_season_id(game_id)
        return SeasonDao(R).fetch_exchange_order(season_id)

    def _fetch_exchange_back_order(self,
                                   game_id: int,
                                   ) -> EExchangeOrder:
        exchange_order = self._fetch_exchange_order(game_id)
        if exchange_order is EExchangeOrder.CLOCKWISE:
            return EExchangeOrder.COUNTERCLOCKWISE
        elif exchange_order is EExchangeOrder.COUNTERCLOCKWISE:
            return EExchangeOrder.CLOCKWISE
        else:
            raise ValueError('Exchange order must be either "CLOCKWISE", '
                             'or "COUNTERCLOCKWISE"')

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

    def check_game_is_finished(self,
                               user_id: int | None = None,
                               game_id: int | None = None,
                               ) -> bool:
        game_id = game_id or self._fetch_game_id_by_user_id(user_id)
        is_finished = self._fetch_model_attr(game_id, 'is_finished')

        return is_finished

    def _prepare_for_next_move(self,
                               game_id: int,
                               ) -> None:
        self._add_season_points(game_id)
        if self._check_season_points_exceeded(game_id):
            self._finish_season(game_id)
            if self._check_last_season_finished(game_id):
                self._finish_game(game_id)
            else:  # finished season is not last
                self._switch_to_next_season(game_id)

    def _finish_season(self,
                       game_id: int,
                       ) -> None:
        season_id = self._fetch_current_season_id(game_id)
        SeasonDao(R).finish_season(season_id)

    def _add_season_points(self,
                           game_id: int,
                           ) -> None:
        season_id = self._fetch_current_season_id(game_id)
        SeasonDao(R).add_season_points(season_id)

    def _check_season_points_exceeded(self,
                                      game_id: int,
                                      ) -> bool:
        current_season_id = self._fetch_current_season_id(game_id)
        points_exceeded = SeasonDao(R).check_season_points_exceeded(
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
        # if there's only place for anomaly, then 'is_on_ruins_allowed' is False
        SeasonDao(R).start_new_move(
            season_id=self._fetch_current_season_id(game_id),
            is_on_ruins_allowed=True,
        )
        self._set_players_move_not_finished(game_id)

    def _check_discovery_card_is_monster(self,
                                         game_id: int,
                                         ) -> bool:
        season_id = self._fetch_current_season_id(game_id)
        return SeasonDao(R).check_discovery_card_is_monster(season_id)

    def _set_players_move_not_finished(self,
                                       game_id: int,
                                       ) -> None:
        player_ids = self._fetch_player_ids(game_id)
        PlayerDao(R).set_players_move_not_finished(player_ids)

    def _switch_to_next_season(self,
                               game_id: int,
                               ) -> None:
        unused_monster_card_ids = SeasonDao(R).fetch_monster_card_ids(
            self._fetch_current_season_id(game_id)
        )
        SeasonDao(R).finish_init_season(
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
        monster_card_ids = MonsterCardDao(R).pick_monster_cards()
        objective_card_ids = ObjectiveCardDao(R).pick_objective_cards()

        initial_cards = InitialCards(terrain_card_ids,
                                     monster_card_ids,
                                     objective_card_ids)

        return initial_cards

    def _check_last_season_finished(self,
                                    game_id: int,
                                    ) -> bool:
        """ Check if game has ended, but it's not indicated in system """
        last_season_id = self._fetch_last_season_id(game_id)
        return SeasonDao(R).check_season_finished(last_season_id)

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

    def _gen_game_field(self) -> FieldRegular:
        field = BLANK_FIELD
        return field


class ObjectiveCardDao(DaoFull):
    OBJECTIVE_CARD_QUANTITY = 4

    _key_schema = ObjectiveCardKeySchema()
    _converter = ObjectiveCardConverter()
    _model_class = ObjectiveCardDC

    def pick_objective_cards(self) -> list[int]:  # it's copypasta!
        card_ids_key = self._key_schema.ids_key
        card_ids = [int(id) for id in self._redis.smembers(card_ids_key)]

        cards: ObjectiveCardsByCategory = {
            name: self._select_cards_by_type(card_ids, category)
            for name, category in zip(
                ('village', 'forest', 'field_and_water', 'formation'),
                (
                    EObjectiveCardCategory.VILLAGE,
                    EObjectiveCardCategory.FOREST,
                    EObjectiveCardCategory.FIELD_AND_WATER,
                    EObjectiveCardCategory.FORMATION,
                )
            )
        }
        picked_card_ids = self._pick_card_for_each_category(cards)
        return picked_card_ids

    def _pick_card_for_each_category(
            self,
            card_ids_by_category: ObjectiveCardsByCategory,
    ) -> list[int]:
        print(card_ids_by_category)
        picked_card_ids = [
            self._pick_card_id(card_ids_by_category['village']),
            self._pick_card_id(card_ids_by_category['forest']),
            self._pick_card_id(card_ids_by_category['field_and_water']),
            self._pick_card_id(card_ids_by_category['formation']),
        ]
        return picked_card_ids

    def _select_cards_by_type(self,
                              card_ids: MutableSequence[int],
                              category: EObjectiveCardCategory,
                              ) -> list[int]:
        res = [
            card_id for card_id in card_ids
            if services.common.get_enum_by_value(
                EObjectiveCardCategory,
                self._fetch_category(card_id),
            ) == category
        ]
        return res

    def _fetch_category(self,
                        card_id: int,
                        ) -> str:
        category_str = self._fetch_model_attr(
            model_id=card_id,
            field_name='category',
            converter=services.utils.decode_bytes,
        )
        category_enum = services.common.get_enum_by_value(
            EObjectiveCardCategory, category_str
        )
        return category_enum

    def fetch_objective_cards_pretty(self,
                                     objective_card_ids: Iterable[int],
                                     ) -> list[ObjectiveCardPretty]:
        return [
            self._fetch_objective_card_pretty(objective_card_id)
            for objective_card_id in objective_card_ids
        ]

    def _fetch_objective_card_pretty(self,
                                     objective_card_id: int,
                                     ) -> ObjectiveCardPretty:
        objective_card_dc: ObjectiveCardDC = self.fetch_dc_model(
            objective_card_id
        )
        return self._converter.dc_model_to_pretty_model(objective_card_dc)


class TerrainCardDao(DiscoveryCardDao):
    TERRAIN_CARD_QUANTITY = 14

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

        return terrain and TERRAIN_STR_TO_NUM[terrain]

    def fetch_additional_terrain_pretty(self,
                                        terrain_card_id: int,
                                        ) -> Optional[int]:
        additional_terrain = self._fetch_model_attr(
            model_id=terrain_card_id,
            field_name='additional_terrain',
            converter=services.utils.decode_bytes,
        )
        # if no add_terrain, then return None
        return additional_terrain and TERRAIN_STR_TO_NUM[additional_terrain]

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

    def pick_card_id(self,
                     card_ids: MutableSequence[int],
                     allow_ruins: bool,
                     ) -> int:
        while True:
            card_id = self._pick_card_id(card_ids)
            if allow_ruins or not self.check_card_is_ruins(card_id):
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
        return TerrainCardDao(R).check_card_type(card_id, 'ruins')

    def check_card_is_anomaly(self,
                              card_id: int,
                              ) -> bool:
        return TerrainCardDao(R).check_card_type(card_id, 'anomaly')

    def check_card_type(self,
                        card_id: int,
                        checked_card_type: str,
                        ) -> bool:
        actual_card_type = self.fetch_card_type(card_id)
        return actual_card_type == checked_card_type


class ShapeDaoRedis(DaoFull):
    _key_schema = ShapeKeySchema()
    _converter = ShapeConverter()
    _model_class = ShapeDC


class SeasonDao(DaoRedis):
    _key_schema = SeasonKeySchema()
    _converter = SeasonConverter()
    _model_class = SeasonDC

    def fetch_move_id(self,
                      season_id: int,
                      ) -> int:
        move_id = self._fetch_model_attr(season_id, 'current_move_id')
        services.utils.validate_not_none(move_id)

        return move_id

    def fetch_objective_cards_pretty(self,
                                     season_ids: MutableSequence[int],
                                     ) -> list[ObjectiveCardPretty]:
        objective_card_ids = self._fetch_objective_card_ids(season_ids)
        return ObjectiveCardDao(R).fetch_objective_cards_pretty(
            objective_card_ids
        )

    def _fetch_objective_card_ids(self,
                                  season_ids: Iterable,
                                  ) -> list[int]:
        objective_card_ids = [
            self._fetch_first_objective_card_id(season_id)
            for season_id in season_ids
        ]
        return objective_card_ids

    def _fetch_first_objective_card_id(self,
                                       season_id: int,
                                       ) -> int:
        return self._fetch_model_attr(season_id, 'objective_card_ids')[0]

    def check_season_finished(self,
                              season_id: int,
                              ) -> bool:
        is_finished = self._fetch_model_attr(season_id, 'is_finished')
        services.utils.validate_not_none(is_finished)

        return is_finished

    def fetch_exchange_order(self,
                             season_id: int,
                             ) -> EExchangeOrder:
        move_id = self.fetch_move_id(season_id)
        return MoveDao(R).fetch_exchange_order(move_id)

    def check_discovery_card_is_monster(self,
                                        season_id: int,
                                        ) -> bool:
        move_id = self.fetch_move_id(season_id)
        return MoveDao(R).check_discovery_card_is_monster(move_id)

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
            terrain_card_ids=self._shuffle_cards(terrain_card_ids),  # no need to shuffle
            # terrain_card_ids=[6] * 10 + [15, 15, 15],
            monster_card_ids=[monster_card_ids.pop()],
            # monster_card_ids=[],
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
            objective_card_ids=[objective_card_ids[3],
                                objective_card_ids[0]],
            terrain_card_ids=self._shuffle_cards(terrain_card_ids),
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

    def _set_discovery_cards(self,
                             season_id: int,
                             terrain_card_ids: MutableSequence[int],
                             monster_card_ids: MutableSequence[int],
                             ) -> None:
        self._set_terrain_card_ids(season_id, terrain_card_ids)
        self._set_monster_card_ids(season_id, monster_card_ids)

    def _set_terrain_card_ids(self,
                              season_id: int,
                              terrain_card_ids: MutableSequence[int],
                              ) -> None:
        self._set_model_attr(season_id, 'terrain_card_ids', terrain_card_ids)

    def _set_monster_card_ids(self,
                              season_id: int,
                              monster_card_ids: MutableSequence[int],
                              ) -> None:
        self._set_model_attr(season_id, 'monster_card_ids', monster_card_ids)

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
        if terrain_card_ids is None:
            terrain_card_ids = self._fetch_terrain_card_ids(season_id)
        if monster_card_ids is None:
            monster_card_ids = self._fetch_monster_card_ids(season_id)

        (card_id,
         card_type,
         is_on_ruins) = DiscoveryCardDao(R).pick_card_and_is_on_ruins(
            terrain_card_ids=terrain_card_ids,
            monster_card_ids=monster_card_ids,
            is_on_ruins_allowed=is_on_ruins_allowed
        )
        season_id and self._set_discovery_cards(season_id,
                                                terrain_card_ids,
                                                monster_card_ids)

        new_move_id = MoveDao(R).init_move(
            discovery_card_id=card_id,
            discovery_card_type=card_type,
            is_on_ruins=is_on_ruins,
        )
        season_id and self._set_current_move_id(season_id, new_move_id)

        return new_move_id

    def add_season_points(self,
                          season_id: int,
                          ) -> None:
        current_points = self._fetch_current_points(season_id)
        move_id = self._fetch_current_move_id(season_id)
        self._set_current_points(
            season_id,
            current_points + MoveDao(R).fetch_season_points(move_id),
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

    def fetch_exchange_order(self,
                             move_id: int,
                             ) -> EExchangeOrder:
        self._validate_discovery_card_is_monster(move_id)
        monster_card_id = self._fetch_discovery_card_id(move_id)
        return MonsterCardDao(R).fetch_exchange_order(monster_card_id)

    def _validate_discovery_card_is_monster(self,
                                            move_id: int,
                                            ) -> None:
        if self._fetch_discovery_card_type(move_id) != 'monster':
            raise ValueError("Discovery card must be monster.")

    def check_discovery_card_is_monster(self,
                                        move_id: int,
                                        ) -> bool:
        return self._fetch_discovery_card_type(move_id) == 'monster'

    def fetch_is_on_ruins(self,
                          move_id: int,
                          ) -> bool:
        is_prev_card_ruins = self._fetch_model_attr(
            model_id=move_id,
            field_name='is_on_ruins',
        )
        services.utils.validate_not_none(is_prev_card_ruins)

        return is_prev_card_ruins

    def fetch_season_points(self,
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
            case 'anomaly' | 'ruins':
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
        return discovery_card_type == 'terrain'

    def _fetch_card_terrain_pretty(self,
                                   move_id: int,
                                   ) -> int:
        card_type = self._fetch_discovery_card_type(move_id)
        match card_type:
            case 'terrain':
                terrain_pretty = TerrainCardDao(R).fetch_terrain_pretty(
                    terrain_card_id=self._fetch_discovery_card_id(move_id)
                )
            case 'monster':
                terrain_pretty = TERRAIN_STR_TO_NUM['monster']
            case _:
                raise ValueError('discovery card type must be '
                                 'either "terrain" or "monster"')

        return terrain_pretty

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
                card_dao = MonsterCardDao(R)
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

        return TerrainCardDao(R).fetch_additional_shape_pretty(card_id)

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
                url = TerrainCardDao(R).fetch_image_url(
                    self._fetch_discovery_card_id(move_id)
                )
            case 'monster':
                url = MonsterCardDao(R).fetch_image_url(
                    self._fetch_discovery_card_id(move_id)
                )
            case _:
                raise ValueError('Type of discovery card must be either '
                                 '"terrain" or "monster"')

        return url

    def _fetch_discovery_card_type(self,
                                   move_id: int,
                                   ) -> str:
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

    def fetch_players_pretty(self,
                             player_ids: Iterable[int],
                             ) -> list[PlayerPretty]:
        players = [
            self._fetch_player_pretty(player_id)
            for player_id in player_ids
        ]
        return players

    def fetch_player_results_pretty(self,
                                    player_ids: Iterable[int],
                                    ) -> list[PlayerResultPretty]:
        return [
            self._fetch_player_result_pretty(player_id)
            for player_id in player_ids
        ]

    def _fetch_player_result_pretty(self,
                                    player_id: int,
                                    ) -> PlayerResultPretty:
        return PlayerResultPretty(
            player=self._fetch_player_pretty(player_id),
            player_field=self.fetch_field_pretty(player_id),
            seasons_score=self.fetch_seasons_score_pretty(player_id=player_id),
        )

    def fetch_seasons_score_pretty(self,
                                   user_id: int | None = None,
                                   player_id: int | None = None,
                                   ) -> SeasonsScorePretty:
        player_id = player_id or self.fetch_player_id_by_user_id(user_id)
        score_id = self._fetch_seasons_score_id(player_id)
        return SeasonsScoreDao(R).fetch_seasons_score_pretty(score_id)

    def fetch_neighbor_field_pretty(self,
                                    player_id: int,
                                    exchange_order: EExchangeOrder,
                                    ) -> FieldPretty:
        if exchange_order is EExchangeOrder.CLOCKWISE:
            field = self._fetch_counterclockwise_player_field(player_id)
        elif exchange_order is EExchangeOrder.COUNTERCLOCKWISE:
            field = self._fetch_clockwise_player_field(player_id)
        else:
            raise ValueError("Exchange order must be either 'clockwise' or "
                             "'counterclockwise'")

        return games.utils.field_regular_to_pretty(field)

    def check_move_already_made(self,
                                user_id: int,
                                ) -> bool:
        player_id = self.fetch_player_id_by_user_id(user_id)
        return self._fetch_is_move_finished(player_id)

    def _fetch_clockwise_player_field(self,
                                      player_id: int,
                                      ) -> FieldRegular:
        clockwise_player_id = self._fetch_clockwise_player_id(player_id)
        return self._fetch_field(clockwise_player_id)

    def _fetch_counterclockwise_player_field(self,
                                             player_id: int,
                                             ) -> FieldRegular:
        counterclockwise_player_id = self._fetch_counterclockwise_player_id(
            player_id
        )
        return self._fetch_field(counterclockwise_player_id)

    def _fetch_clockwise_player_id(self,
                                   player_id: int,
                                   ) -> int:
        return self._fetch_model_attr(player_id, 'clockwise_player_id')

    def _fetch_counterclockwise_player_id(self,
                                          player_id: int,
                                          ) -> int:
        return self._fetch_model_attr(player_id, 'counterclockwise_player_id')

    def _fetch_field(self,
                     player_id: int,
                     ) -> FieldRegular:
        return self._fetch_model_attr(
            model_id=player_id,
            field_name='field',
            converter=games.utils.deserialize_field,
        )

    def _set_clockwise_player_field(self,
                                    player_id: int,
                                    field: FieldRegular,
                                    ) -> None:
        clockwise_player_id = self._fetch_clockwise_player_id(player_id)
        self._set_field(clockwise_player_id, field)

    def _set_counterclockwise_player_field(self,
                                           player_id: int,
                                           field: FieldRegular,
                                           ) -> None:
        counterclockwise_player_id = self._fetch_counterclockwise_player_id(
            player_id
        )
        self._set_field(counterclockwise_player_id, field)

    def _set_neighbor_field(self,
                            player_id: int,
                            updated_field: FieldRegular,
                            exchange_order: EExchangeOrder,
                            ) -> None:
        if exchange_order is EExchangeOrder.CLOCKWISE:
            self._set_counterclockwise_player_field(player_id, updated_field)
        elif exchange_order is EExchangeOrder.COUNTERCLOCKWISE:
            self._set_clockwise_player_field(player_id, updated_field)

    def set_players_move_not_finished(self,
                                      player_ids: Iterable[int],
                                      ) -> None:
        for player_id in player_ids:
            self._set_is_move_finished(player_id, False)

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
                               updated_field: FieldRegular,
                               exchange_order: EExchangeOrder | None,
                               ) -> None:
        if exchange_order:
            self._set_neighbor_field(player_id, updated_field, exchange_order)
        else:
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
        counterclockwise_player: PlayerDC
        clockwise_player: PlayerDC
        counterclockwise_player, clockwise_player = player_dao.fetch_dc_models(
            (counterclockwise_player := player.counterclockwise_player_id,
             clockwise_player := player.clockwise_player_id)
        )

        counterclockwise_player.clockwise_player_id = clockwise_player.id
        clockwise_player.counterclockwise_player_id = counterclockwise_player.id

        self.insert_dc_models((counterclockwise_player, clockwise_player))

    def _fetch_is_move_finished(self,
                                player_id,
                                ) -> bool:
        is_move_finished = self._fetch_model_attr(player_id, 'is_move_finished')
        services.utils.validate_not_none(is_move_finished)

        return is_move_finished

    def _set_field(self,
                   player_id: int,
                   updated_field: FieldRegular,
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
        self._set_model_attr(player_id, 'is_move_finished', value)

    def init_players(self,
                     user_ids: Sequence[int],
                     field: FieldRegular,
                     ) -> list[int]:
        neighbors_lst = self._get_neighbors_lst(user_ids)
        player_ids = [
            self._init_player(neighbors, field)
            for neighbors in neighbors_lst
        ]
        return player_ids

    def fetch_seasons_score_id(self,
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
            converter=lambda x: games.utils.field_regular_to_pretty(
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
            clockwise_player_id_index = (0 if self._is_last_index(player_ids, i)
                                         else i + 1)
            neighbors = Neighbors(
                user_id=user_id,
                clockwise_player_id=player_ids[i - 1],
                player_id=player_id,
                counterclockwise_player_id=player_ids[clockwise_player_id_index],
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
                     field: FieldRegular
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
                      field: FieldRegular,
                      seasons_score_id: int,
                      ) -> PlayerDC:
        player_dc = self._model_class(
            id=neighbors.player_id,
            user_id=neighbors.user_id,
            field=field,
            clockwise_player_id=neighbors.clockwise_player_id,
            counterclockwise_player_id=neighbors.counterclockwise_player_id,
            coins=0,
            seasons_score_id=seasons_score_id,
            is_move_finished=False,
        )
        return player_dc

    def _fetch_player_pretty(self,
                             player_id: int,
                             ) -> PlayerPretty:
        return PlayerPretty(
            id=player_id,
            name=self.fetch_name(player_id),
            score=self.get_score_total(player_id)
        )

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


class MonsterCardDao(DiscoveryCardDao):
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

    def fetch_exchange_order(self,
                             card_id: int,
                             ) -> EExchangeOrder:
        exchange_order = self._fetch_model_attr(
            model_id=card_id,
            field_name='exchange_order',
            converter=services.utils.decode_bytes,
        )
        services.utils.validate_not_none(exchange_order)

        return services.common.get_enum_by_value(EExchangeOrder,
                                                 exchange_order)
