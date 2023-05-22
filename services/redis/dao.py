from services.redis.key_schemas import UserKeySchema
from services.redis.model_transformers import UserTransformer
from services.redis.redis_dao_base import DaoRedisSQL


class UserDaoRedis(DaoRedisSQL):
    _key_schema = UserKeySchema()
    _transformer = UserTransformer()
