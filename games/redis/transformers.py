from games.models import MonsterCardSQL, DiscoveryCardSQL, ETerrainCardType, ETerrainTypeLimited, ObjectiveCardSQL, \
    EExchangeOrder, SeasonCardSQL
from games.redis.dc_models import MonsterCardDC, GameDC, TerrainCardDC, ObjectiveCardDC, MoveDC, PlayerDC, SeasonDC, \
    ESeasonName, SeasonCardDC, EDiscoveryCardType, SpringScoreDC, SummerScoreDC, FallScoreDC, WinterScoreDC, \
    SeasonsScoreDC
from games.redis.dict_models import SeasonDict, MoveDict, PlayerDict, MonsterCardDict, GameDict, TerrainCardDict, \
    ObjectiveCardDict, SpringScoreDict, SummerScoreDict, FallScoreDict, WinterScoreDict, SeasonsScoreDict
from games.redis.hash_models import GameHash, SeasonHash, MonsterCardHash, TerrainCardHash, MoveHash, PlayerHash, \
    ObjectiveCardHash, FallScoreHash, WinterScoreHash, SummerScoreHash, SpringScoreHash, SeasonsScoreHash
from services import utils
from services.redis.transformers_base import BaseRedisTransformer, BaseSQLTransformer, \
    BaseFullTransformer
from services.redis.models_base import get_enum_by_value, HashModel, DataClassModel, DictModel


# TODO: use Converter instead of Transformer


class GameTransformer(BaseRedisTransformer):

    @staticmethod
    def dc_model_to_dict_model(dc_model: GameDC,
                               ) -> GameDict:
        game_dict = GameDict(
            id=dc_model.id,
            room_id=dc_model.room_id,
            admin_id=dc_model.admin_id,
            player_ids=utils.ids_to_str(dc_model.player_ids),
            monster_card_ids=utils.ids_to_str(
                dc_model.monster_card_ids
            ),
            terrain_card_ids=utils.ids_to_str(
                dc_model.terrain_card_ids
            ),
            season_ids=utils.ids_to_str(dc_model.season_ids),
            current_season_id=dc_model.current_season_id,
        )
        return game_dict

    @staticmethod
    def hash_model_to_dc_model(hash_model: GameHash,
                               ) -> GameDC:
        game_dc = GameDC(
            id=int(hash_model[b'id']),
            room_id=int(hash_model[b'room_id']),
            player_ids=utils.bytes_to_list(
                hash_model[b'player_ids']
            ),
            admin_id=int(hash_model[b'admin_id']),
            monster_card_ids=utils.bytes_to_list(
                hash_model[b'monster_card_ids']
            ),
            terrain_card_ids=utils.bytes_to_list(
                hash_model[b'terrain_card_ids']
            ),
            season_ids=utils.bytes_to_list(
                hash_model[b'season_ids']
            ),
            current_season_id=int(hash_model[b'current_season_id']),
        )
        return game_dc


class SeasonTransformer(BaseRedisTransformer):
    """ transformer for seasons but not season_cards """

    @staticmethod
    def dc_model_to_dict_model(dc_model: SeasonDC,
                               ) -> SeasonDict:
        season_dict = SeasonDict(
            id=dc_model.id,
            name=dc_model.name.value,
            image_url=dc_model.image_url,
            points_to_end=dc_model.points_to_end,
            objective_card_ids=utils.ids_to_str(
                dc_model.objective_card_ids
            ),
            terrain_card_ids=utils.ids_to_str(
                dc_model.terrain_card_ids
            ),
            monster_card_ids=utils.ids_to_str(
                dc_model.monster_card_ids
            ),
            current_move_id=dc_model.current_move_id or '',
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
            points_to_end=int(hash_model[b'points_to_end']),
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
        )
        return season_dc


class SeasonCardTransformer(BaseSQLTransformer):  # А нужен ли он мне вообще???

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


class MoveTransformer(BaseRedisTransformer):

    @staticmethod
    def dc_model_to_dict_model(dc_model: MoveDC,
                               ) -> MoveDict:
        move_dict = MoveDict(
            id=dc_model.id,
            is_prev_card_ruins=int(dc_model.is_prev_card_ruins),
            discovery_card_type=dc_model.discovery_card_type.value,
            discovery_card_id=dc_model.discovery_card_id,
            season_points=dc_model.season_points,
        )
        return move_dict

    @staticmethod
    def hash_model_to_dc_model(hash_model: MoveHash,
                               ) -> MoveDC:
        move_dc = MoveDC(
            id=int(hash_model[b'id']),
            is_prev_card_ruins=bool(int(hash_model[b'is_prev_card_ruins'])),
            discovery_card_type=get_enum_by_value(
                EDiscoveryCardType,
                hash_model[b'discovery_card_type'].decode('utf-8'),
            ),
            discovery_card_id=int(hash_model[b'discovery_card_id']),
            season_points=int(hash_model[b'season_points']),
        )
        return move_dc


class PlayerTransformer(BaseRedisTransformer):

    @staticmethod
    def dc_model_to_dict_model(dc_model: PlayerDC,
                               ) -> PlayerDict:
        player_dict = PlayerDict(
            id=dc_model.id,
            user_id=dc_model.user_id,
            field=utils.dump_field(dc_model.field),
            left_player_id=dc_model.left_player_id,
            right_player_id=dc_model.right_player_id,
            score=dc_model.seasons_score_id,
        )
        return player_dict

    @staticmethod
    def hash_model_to_dc_model(a: PlayerHash,
                               ) -> PlayerDC:
        player_dc = PlayerDC(
            id=int(a[b'id']),
            user_id=int(a[b'user_id']),
            field=utils.decode_field(a[b'field']),
            left_player_id=int(a[b'left_player_id']),
            right_player_id=int(a[b'right_player_id']),
            seasons_score_id=int(a[b'score']),
        )
        return player_dc


class MonsterCardTransformer(BaseFullTransformer):

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


class ObjectiveCardTransformer(BaseFullTransformer):

    @staticmethod
    def sql_model_to_dc_model(sql_model: ObjectiveCardSQL,
                              ) -> ObjectiveCardDC:
        objective_card_dc = ObjectiveCardDC(
            id=sql_model.pk,
            name=sql_model.name,
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
        )
        return objective_card_dict

    @staticmethod
    def hash_model_to_dc_model(hash_model: ObjectiveCardHash,
                               ) -> ObjectiveCardDC:
        redis_model = ObjectiveCardDC(
            id=int(hash_model[b'id']),
            name=hash_model[b'name'].decode('utf-8'),
            image_url=hash_model[b'image_url'].decode('utf-8'),
        )
        return redis_model


class TerrainCardTransformer(BaseFullTransformer):
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
                    season_points=None,
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
                season_points='',
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
                season_points=None,
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


class SeasonsScoreTransformer(BaseRedisTransformer):

    @staticmethod
    def dc_model_to_dict_model(dc_model: SeasonsScoreDC,
                               ) -> SeasonsScoreDict:
        season_score_dict = SeasonsScoreDict(
            id=dc_model.id,
            spring_score_id=dc_model.spring_score_id,
            summer_score_id=dc_model.summer_score_id,
            fall_score_id=dc_model.fall_score_id,
            winter_score_id=dc_model.winter_score_id,
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
            total=int(hash_model[b'total'])
        )
        return season_score_dc


class SpringScoreTransformer(BaseRedisTransformer):

    @staticmethod
    def dc_model_to_dict_model(dc_model: SpringScoreDC,
                               ) -> SpringScoreDict:
        res = SpringScoreDict(
            id=dc_model.id,
            from_coins=dc_model.from_coins,
            monsters=dc_model.monsters,
            total=dc_model.total,
            A=dc_model.A,
            B=dc_model.B,
        )
        return res

    @staticmethod
    def hash_model_to_dc_model(hash_model: SpringScoreHash,
                               ) -> SpringScoreDC:
        res = SpringScoreDC(
            id=int(hash_model[b'id']),
            from_coins=int(hash_model[b'from_coins']),
            monsters=int(hash_model[b'monsters']),
            total=int(hash_model[b'total']),
            A=int(hash_model[b'A']),
            B=int(hash_model[b'B']),
        )
        return res


class SummerScoreTransformer(BaseRedisTransformer):

    @staticmethod
    def dc_model_to_dict_model(dc_model: SummerScoreDC,
                               ) -> SummerScoreDict:
        res = SummerScoreDict(
            id=dc_model.id,
            from_coins=dc_model.from_coins,
            monsters=dc_model.monsters,
            total=dc_model.total,
            B=dc_model.B,
            C=dc_model.C,
        )
        return res

    @staticmethod
    def hash_model_to_dc_model(hash_model: SummerScoreHash,
                               ) -> SummerScoreDC:
        res = SummerScoreDC(
            id=int(hash_model[b'id']),
            from_coins=int(hash_model[b'from_coins']),
            monsters=int(hash_model[b'monsters']),
            total=int(hash_model[b'total']),
            B=int(hash_model[b'B']),
            C=int(hash_model[b'C']),
        )
        return res


class FallScoreTransformer(BaseRedisTransformer):

    @staticmethod
    def dc_model_to_dict_model(dc_model: FallScoreDC,
                               ) -> FallScoreDict:
        res = FallScoreDict(
            id=dc_model.id,
            from_coins=dc_model.from_coins,
            monsters=dc_model.monsters,
            total=dc_model.total,
            C=dc_model.C,
            D=dc_model.D,
        )
        return res

    @staticmethod
    def hash_model_to_dc_model(hash_model: FallScoreHash,
                               ) -> FallScoreDC:
        res = FallScoreDC(
            id=int(hash_model[b'id']),
            from_coins=int(hash_model[b'from_coins']),
            monsters=int(hash_model[b'monsters']),
            total=int(hash_model[b'total']),
            C=int(hash_model[b'C']),
            D=int(hash_model[b'D']),
        )
        return res


class WinterScoreTransformer(BaseRedisTransformer):

    @staticmethod
    def dc_model_to_dict_model(dc_model: WinterScoreDC,
                               ) -> WinterScoreDict:
        res = WinterScoreDict(
            id=dc_model.id,
            from_coins=dc_model.from_coins,
            monsters=dc_model.monsters,
            total=dc_model.total,
            D=dc_model.D,
            A=dc_model.A,
        )
        return res

    @staticmethod
    def hash_model_to_dc_model(hash_model: WinterScoreHash,
                               ) -> WinterScoreDC:
        res = WinterScoreDC(
            id=int(hash_model[b'id']),
            from_coins=int(hash_model[b'from_coins']),
            monsters=int(hash_model[b'monsters']),
            total=int(hash_model[b'total']),
            D=int(hash_model[b'D']),
            A=int(hash_model[b'A']),
        )
        return res
