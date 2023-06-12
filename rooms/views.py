from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from rooms.redis.dao import RoomDaoRedis
from cartographers_back.settings import REDIS
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

        dict_rooms = RoomDaoRedis(REDIS).get_page(page, limit)

        return Response(data=dict_rooms, status=status.HTTP_200_OK)


class RoomAPIView(APIView):
    authentication_classes = [TokenAuthentication]

    @staticmethod
    def post(request: Request,
             ) -> Response:
        """ create a room and put the user in it as admin """
        token = request.auth
        data = request.data

        room_dao = RoomDaoRedis(REDIS)
        creator_id = get_user_id_by_token(token)

        # TODO: allow to make a room without a password
        room_dc = room_dao.create_room_dc(
            name=str(data['name']),
            password=str(pw) if (pw := data['password']) is not None else None,
            max_users=int(data['max_users']),
            creator_id=creator_id,
        )
        room_dao.insert_dc_model(room_dc)

        return Response(status=status.HTTP_201_CREATED)

    @staticmethod
    def get(request: Request,
            ) -> Response:
        """ get room data where user is """
        token = request.auth

        user_id = get_user_id_by_token(token)
        room = RoomDaoRedis(REDIS).get_complete_room(user_id=user_id)

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

        RoomDaoRedis(REDIS).delete_by_user_id(user_id)

        return Response(status=status.HTTP_204_NO_CONTENT)


class User(APIView):

    def put(self,
            request: Request,
            ) -> Response:
        """ add user to room """
        token = request.auth
        params = request.query_params
        # need to check for password and users amount
        user_id = get_user_id_by_token(token)
        room_id = params['room_id']

        RoomDaoRedis(REDIS).add_user(room_id, user_id)

        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def delete(request: Request,
               ) -> Response:
        """ kick user (only for admin).
         for now, stick to room option """
        token = request.auth
        params = request.query_params

        kicker_id = get_user_id_by_token(token)
        kick_user_id = int(params['kick_user_id'])

        room_dao = RoomDaoRedis(REDIS)
        room_dao.kick_user(kicker_id=kicker_id,
                           kick_user_id=kick_user_id)

        return Response(status=status.HTTP_200_OK)


class Ready(APIView):
    @staticmethod
    def put(request: Request,
            ) -> Response:
        """ change readiness (in room) state """
        token = request.auth
        room_dao = RoomDaoRedis(REDIS)

        user_id = get_user_id_by_token(token)
        room_id = room_dao.get_room_id_by_user_id(user_id)

        room_dao.change_user_readiness(user_id)
        room = room_dao.get_complete_room(room_id)

        return Response(room, status=status.HTTP_200_OK)


class Leave(APIView):
    @staticmethod
    def delete(request: Request,
               ) -> Response:
        """ leave room """
        token = request.auth
        user_id = get_user_id_by_token(token)

        RoomDaoRedis(REDIS).leave_room(user_id)

        return Response(status=status.HTTP_204_NO_CONTENT)
