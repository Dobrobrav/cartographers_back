from enum import Enum, IntEnum

from django.db import models

from games.common import EObjectiveCardName, ETerrainCardType, ETerrainTypeLimited, EExchangeOrder


# Create your models here.
class ObjectiveCardSQL(models.Model):
    name = models.CharField(
        max_length=30, choices=EObjectiveCardName.choices,
    )
    # text = models.TextField(
    #     blank=True, null=True, default=None,
    # )
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
