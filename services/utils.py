from typing import MutableSequence

from django_redis.serializers import json
from rest_framework.authtoken.models import Token
from rest_framework.utils import json

from games.models import ETerrainTypeAll


def get_user_id_by_token(token: str) -> int:
    token_obj = Token.objects.get(key=token)
    user_id = token_obj.user_id

    return user_id


def ids_to_str(ids: MutableSequence[int],
               ) -> str:
    string = ' '.join(str(id) for id in ids)
    return string


def bytes_to_list(bts: bytes,
                  ) -> list[int]:
    ids = [int(id) for id in bts.decode('utf-8').split()]
    return ids


def dump_field(field: MutableSequence[MutableSequence[ETerrainTypeAll]],
               ) -> str:
    res = json.dumps([
        [val.value for val in row]
        for row in field
    ])
    return res

def decode_field(field: bytes,
                 ) -> list[list[str]]:
    field = decode_bytes(field)
    res = json.loads(field)
    return res


def decode_bytes(bytes_: bytes,
                 ) -> str:
    return bytes_.decode('utf-8')
