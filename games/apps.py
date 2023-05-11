from django.apps import AppConfig


class GamesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'games'

    def ready(self) -> None:
        """ setup redis db """
        from . import utils
        utils.save_models_to_redis()
