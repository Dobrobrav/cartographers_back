from django.contrib.auth.hashers import make_password

from rooms.redis.models import RoomRedis
from services.redis_dao_base import DaoRedis
from services.redis_models_base import RedisModel

#
# def do_job(dao: DaoRedis,
#            **attrs
#            ) -> RedisModel:
#     obj = dao.create_model()


