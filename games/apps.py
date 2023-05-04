from django.apps import AppConfig
import redis


class GamesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'games'

    def ready(self) -> None:
        """ setup redis db """
        from .services import tools
        r = redis.Redis(host='redis',
                        port=6379,
                        db=0)

        tools.load_discovery_cards_to_redis(r=r)
