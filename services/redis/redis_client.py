import redis

client = redis.Redis(host='redis',
                     port=6379,
                     # port=6380,
                     db=0)
