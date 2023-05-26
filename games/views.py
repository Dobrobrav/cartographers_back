from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView

from cartographers_back.settings import REDIS
from games.redis.dao import GameDaoRedis
from services.utils import get_user_id_by_token, check_user_is_admin


# Create your views here.
class GameAPIView(APIView):
    def post(self,
             request: Request,
             ) -> Response:
        """ start game (sends admin) """
        token = request.auth
        data = request.data
        user_id = get_user_id_by_token(token)

        check_user_is_admin(user_id)

        game_dao = GameDaoRedis(REDIS)
        game = game_dao.start_game(user_id)

        return Response(game, status=HTTP_201_CREATED)

    def get(self,
            request: Request,
            ) -> Response:
        """ check if new turn has started """


class MoveAPIView(APIView):
    def put(self,
            request: Request,
            ) -> Response:
        """ make move (place figure) """
