from django.apps import AppConfig
import redis


class GamesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'games'

    def ready(self) -> None:
        """ setup redis db """
        from .services import tools
        redis_client = redis.Redis(host='redis',
                                   port=6379,
                                   db=0)
        tools.save_monster_cards_to_redis(redis_client)
        # tools.load_discovery_cards_to_redis(r=r)
