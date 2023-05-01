from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
import redis


# Create your views here.

@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def set_view(
        request: Request,
        key: str,
        value: str,
) -> Response:
    r = redis.Redis(host='redis', port=6379, db=0)
    r.set(name=key, value=value)

    return Response(status=status.HTTP_200_OK)


@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def get_view(
        request: Request,
        key: str,
) -> Response:
    r = redis.Redis(host='redis', port=6379, db=0)
    res = r.get(name=key)

    return Response(res)
