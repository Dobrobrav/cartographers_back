from enum import IntEnum
from typing import TypeAlias, MutableSequence

from django.db import models

FieldRegular: TypeAlias = MutableSequence[MutableSequence['ETerrainTypeAll']]
# FieldRedis: TypeAlias = MutableSequence[MutableSequence[str]]
FieldPretty: TypeAlias = MutableSequence[MutableSequence[int]]

SeasonName: TypeAlias = str
URL: TypeAlias = str
UserID: TypeAlias = int
ScoreSource: TypeAlias = str
ScoreValue: TypeAlias = int


class ETerrainTypeLimited(models.TextChoices):
    WATER = 'water'
    FIELD = 'field'
    FOREST = 'forest'
    VILLAGE = 'village'


class EShapeUnit(IntEnum):
    FILLED = 1
    BLANK = 0


class EExchangeOrder(models.TextChoices):
    CLOCKWISE = 'clockwise'
    COUNTERCLOCKWISE = 'counterclockwise'


class ETerrainCardType(models.TextChoices):
    REGULAR = 'regular'
    RUINS = 'ruins'
    ANOMALY = 'anomaly'


class ETerrainTypeAll(models.Choices):
    WATER = 'water'
    FIELD = 'field'
    FOREST = 'forest'
    VILLAGE = 'village'
    MONSTER = 'monster'
    MOUNTAIN = 'mountain'
    RUINS = 'ruins'
    BLANK = 'blank'


TERRAIN_STR_TO_NUM: dict[str, int] = {
    'water': 3,
    'field': 4,
    'forest': 1,
    'village': 2,
    'monster': 5,
    'mountain': 6,
    'ruins': 7,
    'blank': 0,
}

TERRAIN_NUM_TO_STR: dict[int, str] = {
    value: key for key, value in TERRAIN_STR_TO_NUM.items()
}


class EObjectiveCardName(models.TextChoices):
    LAKEFOLK_MAP = 'lakefolk_map'
    GOLD_VEIN = 'gold_vein'
    ENCHANTERS_DELL = 'enchanter\'s_dell'
    GREEN_LAND = 'green_land'
    SENTINEL_WOOD = 'sentinel_wood'
    MOUNTAIN_GROVE = 'mountain_grove'
    VAST_PLAINS = 'vast_plains'
    BROKEN_ROADS = 'broken_roads'
    CALDERAS = 'calderas'


TT: TypeAlias = ETerrainTypeAll

BLANK_FIELD = [
    [TT.BLANK] * 11,
    [TT.BLANK] * 3 + [TT.MOUNTAIN, TT.BLANK, TT.RUINS] + [TT.BLANK] * 5,
    [TT.BLANK, TT.RUINS] + [TT.BLANK] * 6 + [TT.MOUNTAIN, TT.RUINS, TT.BLANK],
    [TT.BLANK] * 11,
    [TT.BLANK] * 11,
    [TT.BLANK] * 5 + [TT.MOUNTAIN] + [TT.BLANK] * 5,
    [TT.BLANK] * 11,
    [TT.BLANK] * 11,
    [TT.BLANK, TT.RUINS, TT.MOUNTAIN] + [TT.BLANK] * 6 + [TT.RUINS, TT.BLANK],
    [TT.BLANK] * 5 + [TT.RUINS, TT.BLANK, TT.MOUNTAIN] + [TT.BLANK] * 3,
    [TT.BLANK] * 11,
]
