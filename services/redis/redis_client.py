import redis

redis_client = redis.Redis(host='redis',
                           port=6379,
                           # port=6380,
                           db=0)

# redis_client = redis.Redis(
#     host='oregon-redis.render.com',
#     port=6379,
#     username='red-chfrmbik728sd6hgdmag',
#     password='58dispMPT7kUIfifd0R6eZHzfuIXin0q',
#     ssl=True,
# )
