from django.urls import path

from services.redis.redis_client import redis_client
from . import utils
from .views import GameAPIView, MoveAPIView

# utils.save_models_to_redis()

urlpatterns = [
    path('game/', GameAPIView.as_view()),
    path('move/', MoveAPIView.as_view()),
    # path('kick_user', ),
]
