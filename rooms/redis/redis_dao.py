from .key_schemas import RoomKeySchema
from .model_transformers import RoomTransformer
from services.redis_dao_base import DaoRedis


class RoomDaoRedis(DaoRedis):
    _key_schema = RoomKeySchema()
    _transformer = RoomTransformer()
