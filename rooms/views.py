from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from rooms.redis.dao import RoomDaoRedis
from services.redis.redis_client import redis_client
from services.utils import get_user_id_by_token


# Create your views here.


class Display(APIView):
    def get(self,
            request: Request,
            ) -> Response:
        """ Endpoint for displaying a page of rooms """
        params = request.query_params

        page = int(params['page'])
        limit = int(params['limit'])

        room_hashes = RoomDaoRedis(redis_client).get_page(page=page, limit=limit)
        print(room_hashes)

        return Response(room_hashes)


class RoomAPIView(APIView):
    def post(self,
             request: Request,
             ) -> Response:
        """ Endpoint for creating a room """
        token = request.headers['Auth-Token']
        data = request.data

        room_dao = RoomDaoRedis(redis_client)
        creator_id = get_user_id_by_token(token)

        # TODO: allow to make a room without a password
        room = room_dao.create_room(
            name=data['name'],
            password=data['password'],
            max_users=int(data['max_players']),
            creator_id=creator_id,
        )
        room_dao.insert_redis_model(room)

        return Response()


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
