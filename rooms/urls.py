from django.urls import path

from . import utils
from .views import RoomAPIView, EnterDetails, Search, Delete, \
    KickUser, Ready, Leave, DisplayRoomsAPIView

utils.save_models_to_redis()

urlpatterns = [
    path('', DisplayRoomsAPIView.as_view(), name='rooms'),
    path('room/', RoomAPIView.as_view(), name='room'),
    path('enter_details/', EnterDetails.as_view(), name='enter-details'),
    path('search/', Search.as_view(), name='search'),
    path('delete/', Delete.as_view(), name='delete'),
    path('kick_user/', KickUser.as_view(), name='kick_user'),
    path('ready/', Ready.as_view(), name='ready'),
    path('leave/', Leave.as_view(), name='leave'),
]
