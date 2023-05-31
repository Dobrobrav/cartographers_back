from services.redis.key_schemas import UserKeySchema
from services.redis.transformers import UserTransformer
from services.redis.redis_dao_base import DaoFull


class UserDaoRedis(DaoFull):
    _key_schema = UserKeySchema()
    _transformer = UserTransformer()
