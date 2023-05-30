from typing import Iterable

from django.db.models import Model

from games.models import MonsterCardSQL, DiscoveryCardSQL, ETerrainCardType, ETerrainTypeLimited, ObjectiveCardSQL, \
    EExchangeOrder
from games.redis.models import MonsterCardDC, GameData, TerrainCardDC, ObjectiveCardDC, MoveDC, PlayerDC
from services import utils
from services.redis.model_transformers_base import BaseRedisTransformer, DictModel, HashModel, BaseSQLTransformer
from services.redis.redis_models_base import DataClassModel


class GameTransformer(BaseRedisTransformer):

    @staticmethod
    def dc_model_to_dict_model(dc_model: GameData,
                               ) -> DictModel:
        dict_model = {
            'id': dc_model.id,
            'room_id': dc_model.room_id,
            'admin_id': dc_model.admin_id,
            'player_ids': utils.ids_to_str(dc_model.player_ids),
            'monster_card_ids': utils.ids_to_str(
                dc_model.monster_card_ids
            ),
            'terrain_card_ids': utils.ids_to_str(
                dc_model.terrain_card_ids
            ),
            'season_ids': utils.ids_to_str(dc_model.season_ids),
            'current_season_id': dc_model.current_season_id,
        }
        return dict_model

    @staticmethod
    def hash_model_to_dc_model(hash_model: HashModel,
                               ) -> GameData:
        table = GameData(
            id=int(hash_model[b'id']),
            room_id=int(hash_model[b'lobby_id']),
            player_ids=utils.str_to_ids(
                hash_model[b'player_ids'].decode('utf-8')
            ),
            admin_id=int(hash_model[b'admin_id']),
            monster_card_ids=utils.str_to_ids(
                hash_model[b'monster_card_for_game_ids'].decode('utf-8')
            ),
            terrain_card_ids=utils.str_to_ids(
                hash_model[b'discovery_card_for_game_ids'].decode('utf-8')
            ),
            season_ids=utils.str_to_ids(
                hash_model[b'season_for_game_ids'].decode('utf-8')
            ),
            current_season_id=int(hash_model[b'current_season_id']),
        )
        return table


class SeasonTransformer(BaseRedisTransformer):
    """ transformer for seasons but not season_cards """

    @staticmethod
    def dc_model_to_dict_model(dc_model: DataClassModel,
                               ) -> DictModel:
        pass

    @staticmethod
    def hash_model_to_dc_model(hash_model: DictModel,
                               ) -> DataClassModel:
        pass


class SeasonCardTransformer(BaseSQLTransformer):

    @staticmethod
    def sql_model_to_dc_model(sql_model: Model) -> DictModel:
        ...


class MoveTransformer(BaseRedisTransformer):

    @staticmethod
    def sql_model_to_dict_model(sql_model: Model,
                                ) -> DictModel:
        pass

    @staticmethod
    def dc_model_to_dict_model(dc_model: DataClassModel,
                               ) -> DictModel:
        pass

    @staticmethod
    def hash_model_to_dc_model(hash_model: DictModel,
                               ) -> MoveDC:
        pass


class PlayerTransformer(BaseRedisTransformer):

    @staticmethod
    def dc_model_to_dict_model(dc_model: DataClassModel,
                               ) -> DictModel:
        pass

    @staticmethod
    def hash_model_to_dc_model(hash_model: DictModel,
                               ) -> PlayerDC:
        pass


class MonsterCardTransformer(BaseRedisTransformer, BaseSQLTransformer):

    @staticmethod
    def dc_model_to_dict_model(dc_model: MonsterCardDC,
                               ) -> DictModel:
        monster_card_hash = {
            'id': dc_model.id,
            'name': dc_model.name,
            'image_url': dc_model.image_url,
            'shape': dc_model.shape_id,
            'exchange_order': dc_model.exchange_order,
        }
        return monster_card_hash

    @staticmethod
    def sql_model_to_dc_model(sql_model: MonsterCardSQL,
                              ) -> DictModel:
        monster_card_hash = {
            'id': sql_model.pk,
            'name': sql_model.name,
            'image_url': sql_model.image.url,
            'shape': sql_model.shape.shape_str,
            'exchange_order': sql_model.exchange_order,
        }
        return monster_card_hash

    @staticmethod  # TODO: fix this
    def hash_model_to_dc_model(hash_model: HashModel,
                               ) -> MonsterCardDC:
        card = MonsterCardDC(
            id=int(hash_model[b'id']),
            name=hash_model[b'name'].decode('utf-8'),
            image_url=hash_model[b'image_url'].decode('utf-8'),
            shape_id=int(hash_model[b'shape']),
            exchange_order=EExchangeOrder.get_enum_by_value(
                hash_model[b'exchange_order'].decode('utf-8')
            ),
        )
        return card


class ObjectiveCardTransformer(BaseRedisTransformer, BaseSQLTransformer):

    @staticmethod
    def sql_model_to_dc_model(sql_model: ObjectiveCardSQL,
                              ) -> DictModel:
        dict_model = {
            'id': sql_model.pk,
            'name': sql_model.name,
            'image_url': sql_model.image.url,
        }
        return dict_model

    @staticmethod
    def dc_model_to_dict_model(dc_model: ObjectiveCardDC,
                               ) -> DictModel:
        dict_model = {
            'id': dc_model.id,
            'name': dc_model.name,
            'image_url': dc_model.image_url,
        }
        return dict_model

    @staticmethod
    def hash_model_to_dc_model(hash_model: HashModel,
                               ) -> ObjectiveCardDC:
        redis_model = ObjectiveCardDC(
            id=int(hash_model[b'id']),
            name=hash_model[b'name'].decode('utf-8'),
            image_url=hash_model[b'image_url'].decode('utf-8'),
        )
        return redis_model


class TerrainCardTransformer(BaseRedisTransformer, BaseSQLTransformer):
    @staticmethod
    def sql_model_to_dc_model(sql_model: DiscoveryCardSQL,
                              ) -> DictModel:
        dict_model = {
            'id': sql_model.pk,
            'name': sql_model.name,
            'image_url': sql_model.image.url,
            'card_type': sql_model.card_type,
            'shape_id': sql_model.shape.id,
            'terrain': sql_model.terrain,
            'season_points': sql_model.season_points,
            'additional_shape_id': sql_model.additional_shape.id,
            'additional_terrain': sql_model.additional_terrain,
        }
        return dict_model

    @staticmethod
    def dc_model_to_dict_model(dc_model: TerrainCardDC,
                               ) -> DictModel:
        dict_model = {
            'id': dc_model.id,
            'name': dc_model.name,
            'image_url': dc_model.image_url,
            'card_type': dc_model.card_type.value,
            'shape_id': dc_model.shape_id,
            'terrain': dc_model.terrain,
            'season_points': dc_model.season_points,
            'additional_shape_id': dc_model.additional_shape_id,
            'additional_terrain': dc_model.additional_terrain,
        }
        return dict_model

    @staticmethod
    def hash_model_to_dc_model(hash_model: HashModel,
                               ) -> TerrainCardDC:
        redis_model = TerrainCardDC(
            id=int(hash_model[b'id'].decode('utf-8')),
            name=hash_model[b'name'].decode('utf-8'),
            image_url=hash_model[b'image_url'].decode('utf-8'),
            card_type=ETerrainCardType.get_enum_by_value(
                hash_model[b'card_type'].decode('utf-8')
            ),
            shape_id=int(hash_model[b'shape_id'].decode('utf-8')),
            terrain=ETerrainTypeLimited.get_enum_by_value(
                hash_model[b'terrain'].decode('utf-8')
            ),
            season_points=int(
                hash_model[b'season_points'].decode('utf-8')
            ),
            additional_shape_id=int(
                hash_model[b'additional_shape_id'].decode('utf-8')
            ),
            additional_terrain=ETerrainTypeLimited.get_enum_by_value(
                hash_model[b'additional_terrain'].decode('utf-8')
            ),
        )
        return redis_model
