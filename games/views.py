from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView

from cartographers_back.settings import R
from games.redis.dao import GameDao, PlayerDao
from rooms.redis.dao import RoomDao
from services.utils import get_user_id_by_token


# Create your views here.
class GameAPIView(APIView):
    @staticmethod
    def post(request: Request,
             ) -> Response:
        """ start game (sends admin) """
        token = request.auth
        user_id = get_user_id_by_token(token)

        GameDao(R).try_init_game(user_id)

        return Response(status=HTTP_201_CREATED)

    def get(self,
            request: Request,
            ) -> Response:
        """ get game data for concrete user """
        token = request.auth
        user_id = get_user_id_by_token(token)

        game = GameDao(R).fetch_game_pretty(user_id)

        return Response(data=game, status=status.HTTP_200_OK)


class MoveAPIView(APIView):
    def get(self,
            request: Request,
            ) -> Response:
        """ check if new move has started """
        user_id = get_user_id_by_token(request.auth)
        if GameDao(R).check_is_new_move_started(user_id):
            return Response(True)
        else:
            return Response(False)


    def put(self,
            request: Request,
            ) -> Response:
        """ make move (place figure) """
        user_id = get_user_id_by_token(request.auth)
        updated_field = request.data

        GameDao(R).process_move(user_id, updated_field)

        return Response(status=status.HTTP_205_RESET_CONTENT)


class PlayerAPIView(APIView):
    def delete(self,
               request: Request,
               ) -> Response:
        kicker_id = get_user_id_by_token(request.auth)
        player_to_kick_id = int(request.query_params['player_to_kick_id'])
        user_to_kick = PlayerDao(R).fetch_player_id_by_user_id(player_to_kick_id)

        GameDao(R).try_kick_player(kicker_id, player_to_kick_id)

        return Response(status=status.HTTP_200_OK)


class LeaveAPIView(APIView):
    def delete(self,
               request: Request,
               ) -> Response:
        user_id = get_user_id_by_token(request.auth)
        player_id = PlayerDao(R).fetch_player_id_by_user_id(user_id)

        GameDao(R).try_leave(player_id)
        RoomDao(R).try_leave(user_id)

        return Response(status=status.HTTP_200_OK)


class ListView(APIView):
    def post(self,
             request: Request,
             ) -> Response:
        data = request.data
        print(type(data))
        return Response(status=status.HTTP_200_OK)







