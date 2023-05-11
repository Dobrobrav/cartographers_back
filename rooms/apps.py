from django.apps import AppConfig


class RoomsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rooms'

    def ready(self) -> None:
        """ setup redis db """
        from . import utils
        # tools.save_models_to_redis()
        # tools.load_discovery_cards_to_redis(r=r)
