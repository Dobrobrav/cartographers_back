from services.redis.key_schemas import UserKeySchema
from services.redis.model_transformers import UserTransformer
from services.redis.redis_dao_base import DaoSQL


class UserDaoRedis(DaoSQL):
    _key_schema = UserKeySchema()
    _transformer = UserTransformer()
