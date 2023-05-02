from django.db import models
from django.contrib.postgres import fields


class EDiscoveryCardTerrain(models.TextChoices):
    WATER = 'water'
    FIELD = 'field'
    FOREST = 'forest'
    VILLAGE = 'village'


class EFieldTerrain(models.TextChoices):
    WATER = 'water'
    FIELD = 'field'
    FOREST = 'forest'
    VILLAGE = 'village'
    MONSTER = 'monster'
    MOUNTAIN = 'mountain'
    BLANK = 'blank'


class EDiscoveryCardType(models.TextChoices):
    MOUNTAIN = 'mountain'
    REGULAR = 'regular'





# Create your models here.
class ObjectiveCard(models.Model):
    name = models.CharField(
        max_length=20,
    )
    image = models.ImageField(
        upload_to='objective_cards/',
    )

    def __str__(self) -> str:
        return str(self.name)


class DiscoveryCard(models.Model):
    name = models.CharField(
        max_length=20, default=None, null=True,
    )
    image = models.ImageField(
        upload_to='discovery_cards/',
    )
    card_type = models.CharField(
        choices=EDiscoveryCardType.choices, max_length=20
    )
    shape = models.ForeignKey(
        to='Shape', on_delete=models.CASCADE,
        related_name='main_shape_cards',
    )
    additional_shape = models.ForeignKey(
        to='Shape', on_delete=models.CASCADE, blank=True, null=True,
        related_name='additional_shape_cards',
    )  # blank True - value can be unsigned
    # null is False - value can't be null, it must be meaningful
    terrain = models.CharField(
        choices=EDiscoveryCardTerrain.choices, max_length=20,
    )
    additional_terrain = models.CharField(
        choices=EDiscoveryCardTerrain.choices, max_length=20,
        blank=True, null=True,
    )

    def __str__(self) -> str:
        return str(self.name)


class ExchangeOrder(models.TextChoices):
    CLOCKWISE = 'clockwise'
    COUNTERCLOCKWISE = 'counterclockwise'


class MonsterCard(models.Model):
    name = models.CharField(
        max_length=20, default=None, null=True,
    )
    image = models.ImageField(
        upload_to='monster_cards/', default=None, null=True,
    )
    shape = models.ForeignKey(
        to='Shape', on_delete=models.CASCADE,
    )
    exchange_order = models.CharField(
        choices=ExchangeOrder.choices, max_length=20
    )

    def __str__(self) -> str:
        return str(self.name)


class Shape(models.Model):
    DEFAULT_SHAPE = "000000 000000 000000 000000 000000 000000"

    shape_str = models.CharField(
        max_length=41, default=DEFAULT_SHAPE,
    )
    gives_coin = models.BooleanField()
