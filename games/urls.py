from django.urls import path

from . import utils_upload
from .views import GameAPIView, MoveAPIView, PlayerAPIView, LeaveAPIView, ListView

utils_upload.save_models_to_redis()

urlpatterns = [
    path('game/', GameAPIView.as_view()),
    path('move/', MoveAPIView.as_view()),
    path('player/', PlayerAPIView.as_view()),
    path('leave/', LeaveAPIView.as_view()),
    path('list_test/', ListView.as_view()),
]
