from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from rooms.common import UserNotInRoom
from rooms.redis.dao import RoomDaoRedis
from cartographers_back.settings import R
from services.utils import get_user_id_by_token


# Create your views here.
class DisplayRoomsAPIView(APIView):

    # TODO: add_current_users attr
    @staticmethod
    def get(request: Request,
            ) -> Response:
        """ Endpoint for displaying a page of rooms """
        params = request.query_params

        page = int(params['page'])
        limit = int(params['limit'])

        dict_rooms = RoomDaoRedis(R).fetch_page(page, limit)

        return Response(data=dict_rooms, status=status.HTTP_200_OK)


class RoomAPIView(APIView):
    authentication_classes = [TokenAuthentication]  # is it needed?

    @staticmethod
    def post(request: Request,
             ) -> Response:
        """ create a room and put the user in it as admin """
        token = request.auth
        data = request.data

        room_dao = RoomDaoRedis(R)
        creator_id = get_user_id_by_token(token)

        # TODO: allow to make a room without a password
        room_dao.try_init_room(
            name=str(data['name']),
            password=str(pw) if (pw := data['password']) is not None else None,
            max_users=int(data['max_users']),
            creator_id=creator_id,
        )

        return Response(status=status.HTTP_201_CREATED)

    @staticmethod
    def get(request: Request,
            ) -> Response:
        """ get room data where user is """
        token = request.auth
        user_id = get_user_id_by_token(token)

        try:
            room = RoomDaoRedis(R).fetch_room_pretty(user_id=user_id)
        except UserNotInRoom:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(room, status=status.HTTP_200_OK)


class EnterDetails(APIView):
    pass


class Search(APIView):
    def get(self,
            request: Request,
            ) -> Response:
        """ get rooms by search_value (id or room_name), smart search """


class Delete(APIView):
    @staticmethod
    def delete(request: Request,
               ) -> Response:
        """ delete room by token """
        token = request.auth
        user_id = get_user_id_by_token(token)

        RoomDaoRedis(R).delete_user(user_id)

        return Response(status=status.HTTP_204_NO_CONTENT)


class User(APIView):

    def put(self,
            request: Request,
            ) -> Response:
        """ add user to room """
        token = request.auth
        data = request.data
        # need to check for password and users amount
        user_id = get_user_id_by_token(token)
        room_id = data['room_id']

        RoomDaoRedis(R).add_user(room_id, user_id)

        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def delete(request: Request,
               ) -> Response:
        """ kick user (only for admin).
         for now, stick to room option """
        token = request.auth
        params = request.query_params

        kicker_id = get_user_id_by_token(token)
        user_to_kick_id = int(params['user_to_kick_id'])

        room_dao = RoomDaoRedis(R)
        room_dao.try_kick_user(kicker_id=kicker_id,
                               user_to_kick_id=user_to_kick_id)

        return Response(status=status.HTTP_200_OK)


class Ready(APIView):
    @staticmethod
    def put(request: Request,
            ) -> Response:
        """ change readiness (in room) state """
        token = request.auth

        user_id = get_user_id_by_token(token)
        RoomDaoRedis(R).change_user_is_ready(user_id)

        return Response(status=status.HTTP_200_OK)


class Leave(APIView):
    @staticmethod
    def delete(request: Request,
               ) -> Response:
        """ leave room """
        token = request.auth
        user_id = get_user_id_by_token(token)

        RoomDaoRedis(R).try_leave(user_id)

        return Response(status=status.HTTP_204_NO_CONTENT)
