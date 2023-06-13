from enum import Enum, IntEnum

from django.db import models


class ETerrainTypeLimited(models.TextChoices):
    WATER = 'water'
    FIELD = 'field'
    FOREST = 'forest'
    VILLAGE = 'village'


class EShapeUnit(IntEnum):
    FILLED = 1
    BLANK = 0


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


# Create your models here.
class ObjectiveCardSQL(models.Model):
    name = models.CharField(
        max_length=30, choices=EObjectiveCardName.choices,
    )
    image = models.ImageField(
        upload_to='objective_cards/',
    )

    def __str__(self) -> str:
        return str(self.name)


class DiscoveryCardSQL(models.Model):
    name = models.CharField(
        max_length=20, default=None, null=True,
    )
    image = models.ImageField(
        upload_to='discovery_cards/',
    )
    card_type = models.CharField(
        choices=ETerrainCardType.choices, max_length=20
    )
    shape = models.ForeignKey(
        to='ShapeSQL', on_delete=models.CASCADE,
        related_name='main_shape_cards',
        blank=True, null=True,
    )
    additional_shape = models.ForeignKey(
        to='ShapeSQL', on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='additional_shape_cards',
    )  # blank True - value can be unsigned
    # null is False - value can't be null, it must be meaningful
    terrain = models.CharField(
        choices=ETerrainTypeLimited.choices, max_length=20,
        blank=True, null=True,
    )
    additional_terrain = models.CharField(
        choices=ETerrainTypeLimited.choices, max_length=20,
        blank=True, null=True,
    )
    season_points = models.IntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return str(self.name)


class SeasonCardSQL(models.Model):
    name = models.CharField(max_length=10)
    points_to_end = models.IntegerField()
    image = models.ImageField(upload_to='season_cards/')


class EExchangeOrder(models.TextChoices):
    CLOCKWISE = 'clockwise'
    COUNTERCLOCKWISE = 'counterclockwise'


class MonsterCardSQL(models.Model):
    name = models.CharField(
        max_length=20, default=None, null=True,
    )
    image = models.ImageField(
        upload_to='monster_cards/', default=None, null=True,
    )
    shape = models.ForeignKey(
        to='ShapeSQL', on_delete=models.CASCADE,
    )
    exchange_order = models.CharField(
        choices=EExchangeOrder.choices, max_length=20
    )

    def __str__(self) -> str:
        return str(self.name)


class ShapeSQL(models.Model):
    DEFAULT_SHAPE = "000000 000000 000000 000000 000000 000000"  # костыль

    shape_str = models.CharField(
        max_length=41, default=DEFAULT_SHAPE,
    )
    gives_coin = models.BooleanField()

    def __str__(self) -> str:
        return str(self.shape_str)
