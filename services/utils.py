from json.decoder import JSONDecodeError
from typing import Any

from django_redis.serializers import json
from rest_framework.authtoken.models import Token
from rest_framework.utils import json


class NoneNotAllowed(Exception):
    pass


def get_user_id_by_token(token: str) -> int:
    token_obj = Token.objects.get(key=token)
    user_id = token_obj.user_id

    return user_id


def bytes_to_list(bts: bytes,
                  ) -> list[int]:
    ids = [int(id) for id in bts.decode('utf-8').split()]
    return ids


# TODO: load and dump methods must check incoming value type!
def deserialize(raw: bytes,
                ) -> Any:
    # try:
    res = json.loads(decode_bytes(raw))
    return res
    # except JSONDecodeError:
    #     print(raw)


def serialize(val: Any,
              ) -> str:
    return json.dumps(val)


def decode_bytes(bytes_: bytes,
                 ) -> str:
    return bytes_.decode('utf-8')


def validate_not_none(value: Any) -> None:
    if value is None:
        raise NoneNotAllowed()
