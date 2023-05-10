import redis
from redis.client import Redis

import services.redis_client
from games.models import MonsterCardSQL
from games.redis.dao import MonsterCardDaoRedis


def save_models_to_redis():
    client = services.redis_client.client

