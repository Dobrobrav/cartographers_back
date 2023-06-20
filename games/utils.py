from typing import MutableSequence

from rest_framework.utils import json

from games.common import ETerrainTypeAll, TERRAIN_NUM_TO_STR, Field
from services import utils
from services.common import get_enum_by_value


def serialize_field(field: MutableSequence[MutableSequence[ETerrainTypeAll]],
                    ) -> str:
    res = json.dumps([
        [val.value for val in row]
        for row in field
    ])
    return res


def deserialize_field(field: bytes,
                      ) -> Field:
    field = utils.deserialize(field)
    field_formatted = [
        [get_enum_by_value(ETerrainTypeAll, cell) for cell in row]
        for row in field
    ]
    return field_formatted


def decode_pretty_field(field: MutableSequence[MutableSequence[int]],
                        ) -> list[list[ETerrainTypeAll]]:
    field_formatted = [
        [
            get_enum_by_value(ETerrainTypeAll, TERRAIN_NUM_TO_STR[cell])
            for cell in row
        ]
        for row in field
    ]
    return field_formatted
