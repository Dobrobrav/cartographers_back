from django.urls import path

from . import utils
from .views import RoomAPIView, EnterDetails, Search, Delete, \
    KickUser, Ready, Leave, Display

# utils.save_models_to_redis()

urlpatterns = [
    path('', Display.as_view()),
    path('room/', RoomAPIView.as_view()),
    path('enter_details/', EnterDetails.as_view()),
    path('search/', Search.as_view()),
    path('delete/', Delete.as_view()),
    path('kick_user/', KickUser.as_view()),
    path('ready/', Ready.as_view()),
    path('leave/', Leave.as_view()),
]
