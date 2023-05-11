from rest_framework.authtoken.models import Token
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from rooms.redis.dao import RoomDaoRedis
from services.redis import redis_client
from services.utils import get_user_id_by_token


# Create your views here.
class Display(APIView):
    pass


class RoomAPIView(APIView):
    def post(self,
             request: Request,
             ) -> Response:
        """ Endpoint for creating a room """
        data = request.data
        token = request.headers['Auth-Token']
        print(token)

        room_dao = RoomDaoRedis(redis_client.client)
        admin_id = get_user_id_by_token(token)

        # TODO: allow to make a room without a password
        room = room_dao.create_room(
            name=data['name'],
            password=data['password'],
            max_players=int(data['max_players']),
            admin_id=admin_id,
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
