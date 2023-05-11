from services.redis.redis_dao_base import DaoRedis
from .key_schemas import MonsterCardKeySchema, GameTableKeySchema, SeasonKeySchema, MoveKeySchema, PlayerKeySchema
from .model_transformers import MonsterCardTransformer, GameTableTransformer, SeasonTransformer, MoveTransformer, \
    PlayerTransformer


class GameTableDaoRedis(DaoRedis):
    _key_schema = GameTableKeySchema()
    _transformer = GameTableTransformer()


class SeasonDaoRedis(DaoRedis):
    _key_schema = SeasonKeySchema()
    _transformer = SeasonTransformer()


class MoveDaoRedis(DaoRedis):
    _key_schema = MoveKeySchema()
    _transformer = MoveTransformer()


class PlayerDaoRedis(DaoRedis):
    _key_schema = PlayerKeySchema()
    _transformer = PlayerTransformer()


class MonsterCardDaoRedis(DaoRedis):
    _key_schema = MonsterCardKeySchema()
    _transformer = MonsterCardTransformer()
