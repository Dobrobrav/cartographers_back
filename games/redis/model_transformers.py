from typing import Iterable

from django.db.models import Model

from games.models import MonsterCardSQL
from games.redis.models import MonsterCardRedis, GameTableRedis
from services import utils
from services.redis.model_transformers_base import ITransformer, ModelDict, ModelHash
from services.redis.redis_models_base import RedisModel


class GameTableTransformer(ITransformer):
    def bytes_to_redis_model_many(self,
                                  hashes: Iterable[ModelHash],
                                  ) -> list[GameTableRedis]:
        game_tables = [
            self.bytes_to_redis_model(hash)
            for hash in hashes
        ]
        return game_tables

    @staticmethod
    def bytes_to_redis_model(hash: ModelHash,
                             ) -> GameTableRedis:
        game_table = GameTableRedis(

        )

    @staticmethod
    def redis_model_to_dict(model: GameTableRedis,
                            ) -> ModelDict:
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
    def sql_model_to_dict(model: Model,
                          ) -> ModelDict:
        raise NotImplementedError

    @staticmethod
    def hash_to_model(hash: ModelDict,
                      ) -> GameTableRedis:
        table = GameTableRedis(
            id=int(hash['id']),
            lobby_id=int(hash['lobby_id']),
            monster_card_for_game_ids=utils.str_to_ids(
                hash['monster_card_for_game_ids']
            ),
            discovery_card_for_game_ids=utils.str_to_ids(
                hash['discovery_card_for_game_ids']
            ),
            season_for_game_ids=utils.str_to_ids(
                hash['season_for_game_ids']
            ),
            current_move_id=hash['current_move_id'],
        )
        return table


class SeasonTransformer(ITransformer):
    @staticmethod
    def sql_model_to_dict(model: Model) -> ModelDict:
        pass

    @staticmethod
    def redis_model_to_dict(model: RedisModel) -> ModelDict:
        pass

    @staticmethod
    def hash_to_model(hash: ModelDict) -> RedisModel:
        pass


class MoveTransformer(ITransformer):
    @staticmethod
    def sql_model_to_dict(model: Model) -> ModelDict:
        pass

    @staticmethod
    def redis_model_to_dict(model: RedisModel) -> ModelDict:
        pass

    @staticmethod
    def hash_to_model(hash: ModelDict) -> RedisModel:
        pass


class PlayerTransformer(ITransformer):
    @staticmethod
    def sql_model_to_dict(model: Model) -> ModelDict:
        pass

    @staticmethod
    def redis_model_to_dict(model: RedisModel) -> ModelDict:
        pass

    @staticmethod
    def hash_to_model(hash: ModelDict) -> RedisModel:
        pass


class GameTableTransformer(ITransformer):
    @staticmethod
    def redis_model_to_dict(model: GameTableRedis,
                            ) -> ModelDict:
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
    def sql_model_to_dict(model: Model,
                          ) -> ModelDict:
        raise NotImplementedError

    @staticmethod
    def hash_to_model(hash: ModelDict,
                      ) -> GameTableRedis:
        table = GameTableRedis(
            id=int(hash['id']),
            lobby_id=int(hash['lobby_id']),
            monster_card_for_game_ids=utils.str_to_ids(
                hash['monster_card_for_game_ids']
            ),
            discovery_card_for_game_ids=utils.str_to_ids(
                hash['discovery_card_for_game_ids']
            ),
            season_for_game_ids=utils.str_to_ids(
                hash['season_for_game_ids']
            ),
            current_move_id=hash['current_move_id'],
        )
        return table


class MonsterCardTransformer(ITransformer):
    @staticmethod
    def redis_model_to_dict(model: MonsterCardRedis,
                            ) -> ModelDict:
        monster_card_hash = {
            'id': model.id,
            'name': model.name,
            'image_url': model.image_url,
            'shape': model.shape,
            'exchange_order': model.exchange_order,
        }
        return monster_card_hash

    @staticmethod
    def sql_model_to_dict(model: MonsterCardSQL,
                          ) -> ModelDict:
        monster_card_hash = {
            'id': model.pk,
            'name': model.name,
            'image_url': model.image.url,
            'shape': model.shape.shape_str,
            'exchange_order': model.exchange_order,
        }
        return monster_card_hash

    @staticmethod
    def hash_to_model(model_hash: ModelDict,
                      ) -> MonsterCardRedis:
        card = MonsterCardRedis(
            id=int(model_hash['id']),
            name=model_hash['name'],
            image_url=model_hash['image_url'],
            shape=model_hash['shape'],
            exchange_order=model_hash['exchange_order'],
        )
        return card
