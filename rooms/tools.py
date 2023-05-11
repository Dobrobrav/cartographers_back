import services.redis.redis_client


def save_models_to_redis():
    client = services.redis.redis_client.client

