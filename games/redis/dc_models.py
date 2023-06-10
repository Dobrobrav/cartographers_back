from dataclasses import dataclass
from enum import Enum
from typing import MutableSequence, Optional

from games.models import ETerrainTypeAll, ETerrainTypeLimited, ETerrainCardType, EExchangeOrder
from services.redis.models_base import DataClassModel


class EDiscoveryCardType(str, Enum):
    TERRAIN = 'terrain'
    MONSTER = 'monster'


class ESeasonName(str, Enum):
    SPRING = 'spring'
    SUMMER = 'summer'
    FALL = 'fall'
    WINTER = 'winter'


@dataclass
class GameDC(DataClassModel):
    room_id: int
    admin_id: int
    player_ids: MutableSequence[int]
    monster_card_ids: MutableSequence[int]
    terrain_card_ids: MutableSequence[int]
    season_ids: MutableSequence[int]
    current_season_id: Optional[int]


@dataclass
class SeasonDC(DataClassModel):
    name: ESeasonName
    image_url: str
    points_to_end: int
    objective_card_ids: MutableSequence[int]
    terrain_card_ids: MutableSequence[int]  # make sure it's a copy of set
    monster_card_ids: MutableSequence[int]  # same as above
    current_move_id: Optional[int]


@dataclass
class MoveDC(DataClassModel):
    is_prev_card_ruins: bool
    discovery_card_type: EDiscoveryCardType
    discovery_card_id: int
    season_points: int


@dataclass
class TerrainCardDC(DataClassModel):
    name: str
    image_url: str
    card_type: ETerrainCardType
    shape_id: Optional[int]
    terrain: Optional[ETerrainTypeLimited]
    season_points: Optional[int]
    additional_shape_id: Optional[int]
    additional_terrain: Optional[ETerrainTypeLimited]


@dataclass
class ObjectiveCardDC(DataClassModel):
    name: str
    image_url: str


@dataclass
class PlayerDC(DataClassModel):
    user_id: int
    field: MutableSequence[MutableSequence[ETerrainTypeAll]]
    left_player_id: int
    right_player_id: int
    score: int


@dataclass
class SeasonsScoreDC(DataClassModel):
    spring_score_id: int
    summer_score_id: int
    fall_score_id: int
    winter_score_id: int
    total: int


@dataclass
class SeasonScoreDC(DataClassModel):
    from_coins: int
    monsters: int
    total: int


@dataclass
class SpringScoreDC(SeasonScoreDC):
    A: int
    B: int


@dataclass
class SummerScoreDC(SeasonScoreDC):
    B: int
    C: int


@dataclass
class FallScoreDC(SeasonScoreDC):
    C: int
    D: int


@dataclass
class WinterScoreDC(SeasonScoreDC):
    D: int
    A: int


@dataclass
class MonsterCardDC(DataClassModel):
    name: str
    image_url: str
    shape_id: int
    exchange_order: EExchangeOrder


@dataclass
class SeasonCardDC(DataClassModel):
    name: str
    points_to_end: int
    image_url: str
