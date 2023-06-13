from typing import MutableSequence, Any

from django_redis.serializers import json
from rest_framework.authtoken.models import Token
from rest_framework.utils import json

from games.models import ETerrainTypeAll
from services.redis.models_base import get_enum_by_value


def get_user_id_by_token(token: str) -> int:
    token_obj = Token.objects.get(key=token)
    user_id = token_obj.user_id

    return user_id


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
                 ) -> list[list[ETerrainTypeAll]]:
    field = deserialize(field)
    print(field)
    field_formatted = [
        [get_enum_by_value(ETerrainTypeAll, cell) for cell in row]
        for row in field
    ]
    return field_formatted


# TODO: load and dump methods must check incoming value type!
def deserialize(raw: bytes,
                ) -> Any:
    return json.loads(decode_bytes(raw))


def serialize(val: Any,
              ) -> str:
    return json.dumps(val)


def decode_bytes(bytes_: bytes,
                 ) -> str:
    return bytes_.decode('utf-8')
