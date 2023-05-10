from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from rooms.redis.dao import RoomDaoRedis
from rooms.redis.models import RoomRedis
from services.redis_client import client


# Create your views here.
class Display(APIView):
    pass


class RoomAPIView(APIView):
    def post(self,
             request: Request,
             ) -> Response:
        data = request.data
        headers = request.headers

        room_dao = RoomDaoRedis(redis_client=client)
        room = room_dao.create_room(
            name=data['name'],
            password=request['password'],
            max_players=int(request['max_players']),
            token=headers['token'],  # TODO: make sure there is one in headers.
        )
        room_hash = room_dao.insert_redis_model_single(room)

        return Response(room_hash)


class EnterDetails(APIView):
    pass


class Search(APIView):
    pass


class Delete(APIView):
    pass


class KickUser(APIView):
    pass


class Ready(APIView):
    pass


class Leave(APIView):
    pass
