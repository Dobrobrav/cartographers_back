from django.urls import path

from . import utils_upload
from .views import GameAPIView, MoveAPIView, PlayerAPIView, LeaveAPIView, Result

# utils_upload.save_models_to_redis()

urlpatterns = [
    path('game/', GameAPIView.as_view()),
    path('move/', MoveAPIView.as_view()),
    path('player/', PlayerAPIView.as_view()),
    path('leave/', LeaveAPIView.as_view()),
    path('results/', Result.as_view()),
]
