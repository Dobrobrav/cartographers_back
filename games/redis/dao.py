from services.redis_dao_base import DaoRedis
from .key_schemas import MonsterCardKeySchema
from .model_transformers import MonsterCardTransformer


class MonsterCardDaoRedis(DaoRedis):
    _key_schema = MonsterCardKeySchema()
    _transformer = MonsterCardTransformer()
