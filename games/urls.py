from django.urls import path

from . import utils_upload
from .views import GameAPIView, MoveAPIView

utils_upload.save_models_to_redis()

urlpatterns = [
    path('game/', GameAPIView.as_view()),
    path('move/', MoveAPIView.as_view()),
]
