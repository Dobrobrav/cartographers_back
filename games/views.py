from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from cartographers_back.settings import REDIS
from games.redis.dao import GameDaoRedis


# Create your views here.
class GameAPIView(APIView):
    def post(self,
             request: Request,
             ) -> Response:
        """ start game (sends admin) """
        game_dao = GameDaoRedis(REDIS)
        # game_dao.

    def get(self,
            request: Request,
            ) -> Response:
        """ check if new turn has started """


class MoveAPIView(APIView):
    def put(self,
            request: Request,
            ) -> Response:
        """ make move (place figure) """
