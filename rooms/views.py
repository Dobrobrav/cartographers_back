from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from rooms.redis.redis_models import RoomRedis


# Create your views here.
class Display(APIView):
    pass


class RoomAPIView(APIView):
    def post(self,
             request: Request,
             ) -> Response:
        data = request.data
        do_job(data)



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
