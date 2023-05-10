from django.contrib.auth.hashers import make_password

from rooms.redis.redis_models import RoomRedis
from services.redis_dao_base import DaoRedis
from services.redis_models_base import RedisModel


def do_job(data, dao: DaoRedis):
    room = RoomRedis(
        id=dao._generate_id(),
        name=data['name'],
        max_players=int(data['max_players']),
        password=make_password(data['password']),
    )


def _generate_id(dao: DaoRedis) -> int:
    dao.
