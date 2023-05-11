from django.db.models import Model

from games.models import MonsterCardSQL
from games.redis.models import MonsterCardRedis, GameTableRedis
from services import utils
from services.redis.model_transformers_base import ITransformer, ModelHash
from services.redis.redis_models_base import RedisModel


class GameTableTransformer(ITransformer):
    @staticmethod
    def dump_redis_model(model: GameTableRedis,
                         ) -> ModelHash:
        game_table_hash = {
            'id': model.id,
            'lobby_id': model.lobby_id,
            'monster_card_for_game_ids': utils.ids_to_str(
                model.monster_card_for_game_ids
            ),
            'discovery_card_for_game_ids': utils.ids_to_str(
                model.discovery_card_for_game_ids
            ),
            'season_for_game_ids': utils.ids_to_str(
                model.season_for_game_ids
            ),
            'current_move_id': model.current_move_id,
        }
        return game_table_hash

    @staticmethod
    def dump_sql_model(model: Model,
                       ) -> ModelHash:
        raise NotImplementedError

    @staticmethod
    def load_redis_model(redis_hash: ModelHash,
                         ) -> GameTableRedis:
        table = GameTableRedis(
            id=int(redis_hash['id']),
            lobby_id=int(redis_hash['lobby_id']),
            monster_card_for_game_ids=utils.str_to_ids(
                redis_hash['monster_card_for_game_ids']
            ),
            discovery_card_for_game_ids=utils.str_to_ids(
                redis_hash['discovery_card_for_game_ids']
            ),
            season_for_game_ids=utils.str_to_ids(
                redis_hash['season_for_game_ids']
            ),
            current_move_id=redis_hash['current_move_id'],
        )
        return table


class SeasonTransformer(ITransformer):
    @staticmethod
    def dump_sql_model(model: Model) -> ModelHash:
        pass

    @staticmethod
    def dump_redis_model(model: RedisModel) -> ModelHash:
        pass

    @staticmethod
    def load_redis_model(redis_hash: ModelHash) -> RedisModel:
        pass


class MoveTransformer(ITransformer):
    @staticmethod
    def dump_sql_model(model: Model) -> ModelHash:
        pass

    @staticmethod
    def dump_redis_model(model: RedisModel) -> ModelHash:
        pass

    @staticmethod
    def load_redis_model(redis_hash: ModelHash) -> RedisModel:
        pass


class PlayerTransformer(ITransformer):
    @staticmethod
    def dump_sql_model(model: Model) -> ModelHash:
        pass

    @staticmethod
    def dump_redis_model(model: RedisModel) -> ModelHash:
        pass

    @staticmethod
    def load_redis_model(redis_hash: ModelHash) -> RedisModel:
        pass


class GameTableTransformer(ITransformer):
    @staticmethod
    def dump_redis_model(model: GameTableRedis,
                         ) -> ModelHash:
        game_table_hash = {
            'id': model.id,
            'lobby_id': model.lobby_id,
            'monster_card_for_game_ids': utils.ids_to_str(
                model.monster_card_for_game_ids
            ),
            'discovery_card_for_game_ids': utils.ids_to_str(
                model.discovery_card_for_game_ids
            ),
            'season_for_game_ids': utils.ids_to_str(
                model.season_for_game_ids
            ),
            'current_move_id': model.current_move_id,
        }
        return game_table_hash

    @staticmethod
    def dump_sql_model(model: Model,
                       ) -> ModelHash:
        raise NotImplementedError

    @staticmethod
    def load_redis_model(redis_hash: ModelHash,
                         ) -> GameTableRedis:
        table = GameTableRedis(
            id=int(redis_hash['id']),
            lobby_id=int(redis_hash['lobby_id']),
            monster_card_for_game_ids=utils.str_to_ids(
                redis_hash['monster_card_for_game_ids']
            ),
            discovery_card_for_game_ids=utils.str_to_ids(
                redis_hash['discovery_card_for_game_ids']
            ),
            season_for_game_ids=utils.str_to_ids(
                redis_hash['season_for_game_ids']
            ),
            current_move_id=redis_hash['current_move_id'],
        )
        return table


class MonsterCardTransformer(ITransformer):
    @staticmethod
    def dump_redis_model(model: MonsterCardRedis,
                         ) -> ModelHash:
        monster_card_hash = {
            'id': model.id,
            'name': model.name,
            'image_url': model.image_url,
            'shape': model.shape,
            'exchange_order': model.exchange_order,
        }
        return monster_card_hash

    @staticmethod
    def dump_sql_model(model: MonsterCardSQL,
                       ) -> ModelHash:
        monster_card_hash = {
            'id': model.pk,
            'name': model.name,
            'image_url': model.image.url,
            'shape': model.shape.shape_str,
            'exchange_order': model.exchange_order,
        }
        return monster_card_hash

    @staticmethod
    def load_redis_model(model_hash: ModelHash,
                         ) -> MonsterCardRedis:
        card = MonsterCardRedis(
            id=int(model_hash['id']),
            name=model_hash['name'],
            image_url=model_hash['image_url'],
            shape=model_hash['shape'],
            exchange_order=model_hash['exchange_order'],
        )
        return card


