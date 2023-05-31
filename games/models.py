from django.db import models
from typing_extensions import Self


class ETerrainTypeLimited(models.TextChoices):
    WATER = 'water'
    FIELD = 'field'
    FOREST = 'forest'
    VILLAGE = 'village'

    @classmethod
    def get_enum_by_value(cls,
                          value: str,
                          ) -> Self:
        type_ = cls.__new__(cls, value)
        return type_


class ETerrainCardType(models.TextChoices):
    REGULAR = 'regular'
    RUINS = 'ruins'
    ANOMALY = 'anomaly'

    @classmethod
    def get_enum_by_value(cls,
                          value: str,
                          ) -> Self:
        type_ = cls.__new__(cls, value)
        return type_


class ETerrainType(models.TextChoices):
    WATER = 'water'
    FIELD = 'field'
    FOREST = 'forest'
    VILLAGE = 'village'
    MONSTER = 'monster'
    MOUNTAIN = 'mountain'
    RUINS = 'ruins'
    BLANK = 'blank'


class EObjectiveCardName(models.TextChoices):
    GREEN_LAND = 'green_land'


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
    season_points = models.IntegerField(default=3)

    def __str__(self) -> str:
        return str(self.name)


class SeasonCardSQL(models.Model):
    name = models.CharField(max_length=10)
    points_to_end = models.IntegerField()
    image = models.ImageField(upload_to='season_cards/')


class EExchangeOrder(models.TextChoices):
    CLOCKWISE = 'clockwise'
    COUNTERCLOCKWISE = 'counterclockwise'

    @classmethod
    def get_enum_by_value(cls,
                          value: str,
                          ) -> Self:
        type_ = cls.__new__(cls, value)
        return type_


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
    DEFAULT_SHAPE = "000000 000000 000000 000000 000000 000000"

    shape_str = models.CharField(
        max_length=41, default=DEFAULT_SHAPE,
    )
    gives_coin = models.BooleanField()

    def __str__(self) -> str:
        return str(self.shape_str)
