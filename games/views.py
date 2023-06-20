from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView

from cartographers_back.settings import REDIS
from games.redis.dao import GameDaoRedis
from rooms.redis.dao import RoomDaoRedis
from services.utils import get_user_id_by_token


# Create your views here.
class GameAPIView(APIView):
    @staticmethod
    def post(request: Request,
             ) -> Response:
        """ start game (sends admin) """
        token = request.auth
        user_id = get_user_id_by_token(token)

        RoomDaoRedis(REDIS).check_user_is_admin(user_id)
        GameDaoRedis(REDIS).try_init_game(user_id)

        return Response(status=HTTP_201_CREATED)

    def get(self,
            request: Request,
            ) -> Response:
        """ get game data for concrete user """
        token = request.auth
        user_id = get_user_id_by_token(token)

        game = GameDaoRedis(REDIS).get_game_pretty(user_id)

        return Response(data=game, status=status.HTTP_200_OK)


class MoveAPIView(APIView):
    def put(self,
            request: Request,
            ) -> Response:
        """ make move (place figure) """
        user_id = get_user_id_by_token(request.auth)
        updated_field = request.data['field']

        GameDaoRedis(REDIS).make_move(user_id, updated_field)

        return Response(status=status.HTTP_205_RESET_CONTENT)


