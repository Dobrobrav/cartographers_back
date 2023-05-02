from django.urls import path
from .views import GameAPIView, MoveAPIView

urlpatterns = [
    path('game/', GameAPIView.as_view()),
    path('move/', MoveAPIView.as_view()),
    # path('kick_user', ),
]
