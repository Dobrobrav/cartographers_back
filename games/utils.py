import pprint
from typing import MutableSequence

from rest_framework.utils import json

from games.common import ETerrainTypeAll, TERRAIN_NUM_TO_STR, FieldRegular, FieldPretty, TERRAIN_STR_TO_NUM
from services import utils
from services.common import get_enum_by_value


def serialize_field(field: FieldRegular,
                    ) -> str:
    res = json.dumps([
        [val.value for val in row]
        for row in field
    ])
    return res


def deserialize_field(field: bytes,
                      ) -> FieldRegular:
    field = utils.deserialize(field)
    field_formatted = [
        [get_enum_by_value(ETerrainTypeAll, cell) for cell in row]
        for row in field
    ]
    return field_formatted


def field_pretty_to_regular(field: FieldPretty,
                            ) -> FieldRegular:
    field_formatted = [
        [
            get_enum_by_value(ETerrainTypeAll, TERRAIN_NUM_TO_STR[cell])
            for cell in row
        ]
        for row in field
    ]
    return field_formatted


def field_regular_to_pretty(field: FieldRegular,
                            ) -> FieldPretty:
    field_pretty = [
        [TERRAIN_STR_TO_NUM[cell.value] for cell in row]
        for row in field
    ]
    return field_pretty
