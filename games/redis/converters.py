import services
from games.common import EShapeUnit
from games.models import MonsterCardSQL, DiscoveryCardSQL, ETerrainCardType, ETerrainTypeLimited, ObjectiveCardSQL, \
    EExchangeOrder, SeasonCardSQL, ShapeSQL
from games.redis.dc_models import MonsterCardDC, GameDC, TerrainCardDC, ObjectiveCardDC, MoveDC, PlayerDC, SeasonDC, \
    ESeasonName, SeasonCardDC, EDiscoveryCardType, SeasonsScoreDC, SeasonScoreDC, ShapeDC
from games.redis.dict_models import SeasonDict, MoveDict, PlayerDict, MonsterCardDict, GameDict, TerrainCardDict, \
    ObjectiveCardDict, SeasonsScoreDict, \
    SeasonScoreDict, ShapeDict
from games.redis.hash_models import GameHash, SeasonHash, MonsterCardHash, TerrainCardHash, MoveHash, PlayerHash, \
    ObjectiveCardHash, SeasonsScoreHash, \
    SeasonScoreHash, ShapeHash
from services import utils
from services.common import get_enum_by_value
from services.redis.base.converters_base import BaseRedisConverter, BaseSQLConverter, \
    BaseFullConverter
import games.utils


# TODO: use Converter instead of Converter


class GameConverter(BaseRedisConverter):

    @staticmethod
    def dc_model_to_dict_model(dc_model: GameDC,
                               ) -> GameDict:
        game_dict = GameDict(
            id=dc_model.id,
            room_id=dc_model.room_id,
            admin_id=dc_model.admin_id,
            player_ids=utils.serialize(dc_model.player_ids),
            monster_card_ids=utils.serialize(dc_model.monster_card_ids),
            terrain_card_ids=utils.serialize(dc_model.terrain_card_ids),
            season_ids=utils.serialize(dc_model.season_ids),
            current_season_id=dc_model.current_season_id,
            last_season_id=dc_model.last_season_id,
            is_finished=services.utils.serialize(dc_model.is_finished),
        )
        return game_dict

    @staticmethod
    def hash_model_to_dc_model(hash_model: GameHash,
                               ) -> GameDC:
        game_dc = GameDC(
            id=int(hash_model[b'id']),
            room_id=int(hash_model[b'room_id']),
            player_ids=utils.deserialize(hash_model[b'player_ids']),
            admin_id=int(hash_model[b'admin_id']),
            monster_card_ids=utils.deserialize(hash_model[b'monster_card_ids']),
            terrain_card_ids=utils.deserialize(hash_model[b'terrain_card_ids']),
            season_ids=utils.deserialize(hash_model[b'season_ids']),
            current_season_id=int(hash_model[b'current_season_id']),
            last_season_id=int(hash_model[b'last_season_id']),
            is_finished=services.utils.deserialize(hash_model[b'is_finished']),
        )
        return game_dc


class SeasonConverter(BaseRedisConverter):
    """ Converter for seasons but not season_cards """

    @staticmethod
    def dc_model_to_dict_model(dc_model: SeasonDC,
                               ) -> SeasonDict:
        season_dict = SeasonDict(
            id=dc_model.id,
            name=dc_model.name.value,
            image_url=dc_model.image_url,
            current_points=dc_model.current_points,
            max_points=dc_model.max_points,
            objective_card_ids=utils.serialize(
                dc_model.objective_card_ids
            ),
            terrain_card_ids=utils.serialize(
                dc_model.terrain_card_ids
            ),
            monster_card_ids=utils.serialize(
                dc_model.monster_card_ids
            ),
            current_move_id=dc_model.current_move_id or '',
            is_finished=services.utils.serialize(dc_model.is_finished),
        )
        return season_dict

    @staticmethod
    def hash_model_to_dc_model(hash_model: SeasonHash,
                               ) -> SeasonDC:
        season_dc = SeasonDC(
            id=int(hash_model[b'id']),
            name=get_enum_by_value(
                ESeasonName, hash_model[b'name'].decode('utf-8')
            ),
            image_url=hash_model[b'image_url'].decode('utf-8'),
            current_points=int(hash_model[b'current_points']),
            max_points=int(hash_model[b'max_points']),
            objective_card_ids=utils.bytes_to_list(
                hash_model[b'objective_card_ids']
            ),
            terrain_card_ids=utils.bytes_to_list(
                hash_model[b'terrain_card_ids']
            ),
            monster_card_ids=utils.bytes_to_list(
                hash_model[b'monster_card_ids']
            ),
            current_move_id=int(hash_model[b'current_move_id']),
            is_finished=services.utils.deserialize(
                hash_model[b'is_finished']
            )
        )
        return season_dc


class SeasonCardConverter(BaseSQLConverter):  # А нужен ли он мне вообще???

    @staticmethod
    def sql_model_to_dc_model(sql_model: SeasonCardSQL,
                              ) -> SeasonCardDC:
        season_card_dc = SeasonCardDC(
            id=sql_model.pk,
            name=sql_model.name,
            points_to_end=sql_model.points_to_end,
            image_url=sql_model.image.url,
        )
        return season_card_dc


class MoveConverter(BaseRedisConverter):

    @staticmethod
    def dc_model_to_dict_model(dc_model: MoveDC,
                               ) -> MoveDict:
        move_dict = MoveDict(
            id=dc_model.id,
            is_on_ruins=services.utils.serialize(dc_model.is_on_ruins),
            discovery_card_type=dc_model.discovery_card_type.value,
            discovery_card_id=dc_model.discovery_card_id,
        )
        return move_dict

    @staticmethod
    def hash_model_to_dc_model(hash_model: MoveHash,
                               ) -> MoveDC:
        move_dc = MoveDC(
            id=int(hash_model[b'id']),
            is_on_ruins=services.utils.deserialize(
                hash_model[b'is_on_ruins']
            ),
            discovery_card_type=get_enum_by_value(
                EDiscoveryCardType,
                hash_model[b'discovery_card_type'].decode('utf-8'),
            ),
            discovery_card_id=int(hash_model[b'discovery_card_id']),
        )
        return move_dc


class PlayerConverter(BaseRedisConverter):

    @staticmethod
    def dc_model_to_dict_model(dc_model: PlayerDC,
                               ) -> PlayerDict:
        player_dict = PlayerDict(
            id=dc_model.id,
            user_id=dc_model.user_id,
            field=games.utils.serialize_field(dc_model.field),
            left_player_id=dc_model.left_player_id,
            right_player_id=dc_model.right_player_id,
            coins=dc_model.coins,
            seasons_score_id=dc_model.seasons_score_id,
            is_move_finished=utils.serialize(dc_model.is_move_finished),
        )
        return player_dict

    @staticmethod
    def hash_model_to_dc_model(hash_model: PlayerHash,
                               ) -> PlayerDC:
        player_dc = PlayerDC(
            id=int(hash_model[b'id']),
            user_id=int(hash_model[b'user_id']),
            field=games.utils.deserialize_field(hash_model[b'field']),
            left_player_id=int(hash_model[b'left_player_id']),
            right_player_id=int(hash_model[b'right_player_id']),
            coins=int(hash_model[b'coins']),
            seasons_score_id=int(hash_model[b'seasons_score_id']),
            is_move_finished=utils.deserialize(hash_model[b'is_move_finished']),
        )
        return player_dc


class MonsterCardConverter(BaseFullConverter):

    @staticmethod
    def dc_model_to_dict_model(dc_model: MonsterCardDC,
                               ) -> MonsterCardDict:
        monster_card_dict = MonsterCardDict(
            id=dc_model.id,
            name=dc_model.name,
            image_url=dc_model.image_url,
            shape_id=dc_model.shape_id,
            exchange_order=dc_model.exchange_order,
        )
        return monster_card_dict

    @staticmethod
    def sql_model_to_dc_model(sql_model: MonsterCardSQL,
                              ) -> MonsterCardDC:
        monster_card_dc = MonsterCardDC(
            id=sql_model.pk,
            name=sql_model.name,
            image_url=sql_model.image.url,
            shape_id=sql_model.shape_id,
            exchange_order=get_enum_by_value(
                EExchangeOrder,
                sql_model.exchange_order,
            ),
        )
        return monster_card_dc

    @staticmethod
    def hash_model_to_dc_model(hash_model: MonsterCardHash,
                               ) -> MonsterCardDC:
        card = MonsterCardDC(
            id=int(hash_model[b'id']),
            name=hash_model[b'name'].decode('utf-8'),
            image_url=hash_model[b'image_url'].decode('utf-8'),
            shape_id=int(hash_model[b'shape_id']),
            exchange_order=get_enum_by_value(
                EExchangeOrder,
                hash_model[b'exchange_order'].decode('utf-8'),
            ),
        )
        return card


class ObjectiveCardConverter(BaseFullConverter):

    @staticmethod
    def sql_model_to_dc_model(sql_model: ObjectiveCardSQL,
                              ) -> ObjectiveCardDC:
        objective_card_dc = ObjectiveCardDC(
            id=sql_model.pk,
            name=sql_model.name,
            text='SOME PLACEHOLDER',
            image_url=sql_model.image.url,
        )
        return objective_card_dc

    @staticmethod
    def dc_model_to_dict_model(dc_model: ObjectiveCardDC,
                               ) -> ObjectiveCardDict:
        objective_card_dict = ObjectiveCardDict(
            id=dc_model.id,
            name=dc_model.name,
            image_url=dc_model.image_url,
            text=dc_model.text,
        )
        return objective_card_dict

    @staticmethod
    def hash_model_to_dc_model(hash_model: ObjectiveCardHash,
                               ) -> ObjectiveCardDC:
        redis_model = ObjectiveCardDC(
            id=int(hash_model[b'id']),
            name=hash_model[b'name'].decode('utf-8'),
            image_url=hash_model[b'image_url'].decode('utf-8'),
            text='Lorem ipsum dolor sit amet',
        )
        return redis_model


class TerrainCardConverter(BaseFullConverter):
    @staticmethod
    def sql_model_to_dc_model(sql_model: DiscoveryCardSQL,
                              ) -> TerrainCardDC:
        card_type = get_enum_by_value(
            ETerrainCardType,
            sql_model.card_type,
        )

        match card_type:
            case ETerrainCardType.RUINS | ETerrainCardType.ANOMALY:
                terrain_card_dc = TerrainCardDC(
                    id=sql_model.pk,
                    name=sql_model.name,
                    image_url=sql_model.image.url,
                    card_type=card_type,
                    shape_id=None,
                    terrain=None,
                    season_points=0,
                    additional_shape_id=None,
                    additional_terrain=None,
                )
            case ETerrainCardType.REGULAR:
                terrain_card_dc = TerrainCardDC(
                    id=sql_model.pk,
                    name=sql_model.name,
                    image_url=sql_model.image.url,
                    card_type=card_type,
                    shape_id=sql_model.shape_id,
                    terrain=get_enum_by_value(
                        ETerrainTypeLimited,
                        sql_model.terrain,
                    ),
                    season_points=sql_model.season_points,
                    additional_shape_id=sql_model.additional_shape_id,
                    additional_terrain=get_enum_by_value(
                        ETerrainTypeLimited,
                        sql_model.additional_terrain,
                    ) if sql_model.additional_terrain else None,
                )
            case _:
                raise ValueError('terrain card must either ruins or regular')

        return terrain_card_dc

    # TODO: rewrite all ''s in redis to 'null's in redis using json.dumps(None)
    @staticmethod
    def dc_model_to_dict_model(dc_model: TerrainCardDC,
                               ) -> TerrainCardDict:
        card_type = dc_model.card_type

        if card_type in (ETerrainCardType.RUINS, ETerrainCardType.ANOMALY):
            terrain_card_dict = TerrainCardDict(
                id=dc_model.id,
                name=dc_model.name,
                image_url=dc_model.image_url,
                card_type=card_type.value,
                shape_id='',
                terrain='',
                season_points=dc_model.season_points,
                additional_shape_id='',
                additional_terrain='',
            )
        elif card_type is ETerrainCardType.REGULAR:
            terrain_card_dict = TerrainCardDict(
                id=dc_model.id,
                name=dc_model.name,
                image_url=dc_model.image_url,
                card_type=card_type.value,
                shape_id=dc_model.shape_id,
                terrain=dc_model.terrain.value,
                season_points=dc_model.season_points,
                additional_shape_id=dc_model.additional_shape_id or '',
                additional_terrain=dc_model.additional_terrain or '',
            )
        else:
            raise ValueError('terrain card must either ruins or regular')

        return terrain_card_dict

    @staticmethod
    def hash_model_to_dc_model(hash_model: TerrainCardHash,
                               ) -> TerrainCardDC:
        card_type = get_enum_by_value(
            ETerrainCardType,
            hash_model[b'card_type'].decode('utf-8'),
        )

        if card_type is ETerrainCardType.RUINS:
            terrain_card_dc = TerrainCardDC(
                id=int(hash_model[b'id'].decode('utf-8')),
                name=hash_model[b'name'].decode('utf-8'),
                image_url=hash_model[b'image_url'].decode('utf-8'),
                card_type=get_enum_by_value(
                    ETerrainCardType,
                    hash_model[b'card_type'].decode('utf-8')
                ),
                shape_id=None,
                terrain=None,
                season_points=services.utils.deserialize(
                    hash_model[b'season_points']
                ),
                additional_shape_id=None,
                additional_terrain=None,
            )
        elif card_type is ETerrainCardType.REGULAR:
            terrain_card_dc = TerrainCardDC(
                id=int(hash_model[b'id'].decode('utf-8')),
                name=hash_model[b'name'].decode('utf-8'),
                image_url=hash_model[b'image_url'].decode('utf-8'),
                card_type=get_enum_by_value(
                    ETerrainCardType,
                    hash_model[b'card_type'].decode('utf-8'),
                ),
                shape_id=int(hash_model[b'shape_id'].decode('utf-8')),
                terrain=get_enum_by_value(
                    ETerrainTypeLimited,
                    hash_model[b'terrain'].decode('utf-8'),
                ),
                season_points=int(hash_model[b'season_points']),
                additional_shape_id=int(id) if (
                    id := hash_model[b'additional_shape_id']
                ) else None,
                additional_terrain=get_enum_by_value(
                    ETerrainTypeLimited,
                    hash_model[b'additional_terrain'].decode('utf-8'),
                ),
            )
        else:
            raise ValueError('terrain card must either ruins or regular')

        return terrain_card_dc


class ShapeConverter(BaseFullConverter):

    @staticmethod
    def dc_model_to_dict_model(dc_model: ShapeDC,
                               ) -> ShapeDict:
        shape_dict = ShapeDict(
            id=dc_model.id,
            shape_value=utils.serialize(dc_model.shape_value),
            gives_coin=utils.serialize(dc_model.gives_coin),
        )
        return shape_dict

    def hash_model_to_dc_model(self,
                               hash_model: ShapeHash,
                               ) -> ShapeDC:
        shape_dc = ShapeDC(
            id=int(hash_model[b'id']),
            shape_value=self.deserialize_shape_value(
                hash_model[b'shape_value']
            ),
            gives_coin=utils.deserialize(hash_model[b'gives_coin']),
        )
        return shape_dc

    def sql_model_to_dc_model(self,
                              sql_model: ShapeSQL,
                              ) -> ShapeDC:
        shape_dc = ShapeDC(
            id=sql_model.id,
            shape_value=self._deserialize_shape_value_sql(
                sql_model.shape_str
            ),
            gives_coin=sql_model.gives_coin,
        )
        return shape_dc

    @staticmethod
    def _deserialize_shape_value_sql(shape_value_sql: str,
                                     ) -> list[list[EShapeUnit]]:
        res = [
            [
                get_enum_by_value(EShapeUnit, int(unit))
                for unit in list(row)
            ]
            for row in shape_value_sql.split()
        ]
        return res

    @staticmethod
    def deserialize_shape_value(shape_value_raw: bytes,
                                ) -> list[list[EShapeUnit]]:
        shape_value = utils.deserialize(shape_value_raw)
        shape_value_formatted = [
            [get_enum_by_value(EShapeUnit, unit) for unit in row]
            for row in shape_value
        ]
        return shape_value_formatted


class SeasonsScoreConverter(BaseRedisConverter):

    @staticmethod
    def dc_model_to_dict_model(dc_model: SeasonsScoreDC,
                               ) -> SeasonsScoreDict:
        season_score_dict = SeasonsScoreDict(
            id=dc_model.id,
            spring_score_id=dc_model.spring_score_id,
            summer_score_id=dc_model.summer_score_id,
            fall_score_id=dc_model.fall_score_id,
            winter_score_id=dc_model.winter_score_id,
            coins=dc_model.coins,
            total=dc_model.total,
        )
        return season_score_dict

    @staticmethod
    def hash_model_to_dc_model(hash_model: SeasonsScoreHash,
                               ) -> SeasonsScoreDC:
        season_score_dc = SeasonsScoreDC(
            id=int(hash_model[b'id']),
            spring_score_id=int(hash_model[b'spring_score_id']),
            summer_score_id=int(hash_model[b'summer_score_id']),
            fall_score_id=int(hash_model[b'fall_score_id']),
            winter_score_id=int(hash_model[b'winter_score_id']),
            coins=int(hash_model[b'coins']),
            total=int(hash_model[b'total']),
        )
        return season_score_dc


class SeasonScoreConverter(BaseRedisConverter):

    @staticmethod
    def dc_model_to_dict_model(dc_model: SeasonScoreDC,
                               ) -> SeasonScoreDict:
        res = SeasonScoreDict(
            id=dc_model.id,
            from_coins=dc_model.from_coins,
            monsters=dc_model.monsters,
            from_first_task=dc_model.from_first_task,
            from_second_task=dc_model.from_second_task,
            total=dc_model.total,
        )
        return res

    @staticmethod
    def hash_model_to_dc_model(hash_model: SeasonScoreHash,
                               ) -> SeasonScoreDC:
        res = SeasonScoreDC(
            id=int(hash_model[b'id']),
            from_coins=int(hash_model[b'from_coins']),
            monsters=int(hash_model[b'monsters']),
            from_first_task=int(hash_model[b'from_first_task']),
            from_second_task=int(hash_model[b'from_second_task']),
            total=int(hash_model[b'total']),
        )
        return res
