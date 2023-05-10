import redis
from redis.client import Redis

from games.models import MonsterCardSQL
from games.redis.dao import MonsterCardDaoRedis


def save_models_to_redis():
    client = redis.Redis(host='redis',
                         port=6379,
                         db=0)

