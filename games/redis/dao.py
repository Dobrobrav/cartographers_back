from services.redis.redis_dao_base import DaoRedisRedis, DaoRedisSQL
from .key_schemas import MonsterCardKeySchema, GameTableKeySchema, SeasonKeySchema, MoveKeySchema, PlayerKeySchema
from .model_transformers import MonsterCardTransformer, GameTableTransformer, SeasonTransformer, MoveTransformer, \
    PlayerTransformer


class GameTableDaoRedis(DaoRedisRedis):
    _key_schema = GameTableKeySchema()
    _transformer = GameTableTransformer()


class SeasonDaoRedis(DaoRedisRedis):
    _key_schema = SeasonKeySchema()
    _transformer = SeasonTransformer()


class MoveDaoRedis(DaoRedisRedis):
    _key_schema = MoveKeySchema()
    _transformer = MoveTransformer()


class PlayerDaoRedis(DaoRedisRedis):
    _key_schema = PlayerKeySchema()
    _transformer = PlayerTransformer()


class MonsterCardDaoRedis(DaoRedisRedis, DaoRedisSQL):
    _key_schema = MonsterCardKeySchema()
    _transformer = MonsterCardTransformer()
