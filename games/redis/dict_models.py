from typing import MutableSequence, Optional

from games.models import ETerrainCardType, ETerrainTypeLimited, ETerrainType, EExchangeOrder
from games.redis.dc_models import ESeasonName, EDiscoveryCardType
from services.redis.models_base import DictModel


class GameDict(DictModel):
    id: int
    room_id: int
    admin_id: int
    player_ids: str
    monster_card_ids: str
    terrain_card_ids: str
    season_ids: str
    current_season_id: Optional[int]


class SeasonDict(DictModel):
    id: int
    name: str
    ending_points: int
    objective_card_ids: str
    terrain_card_ids: str  # make sure it's a copy of set
    monster_card_ids: str  # same as above
    current_move_id: Optional[int]


class MoveDict(DictModel):
    id: int
    is_prev_card_ruins: bool
    discovery_card_type: str
    discovery_card_id: int
    season_points: int


class TerrainCardDict(DictModel):
    id: int
    name: str
    image_url: str
    card_type: str
    shape_id: int
    terrain: str
    season_points: int
    additional_shape_id: Optional[int]
    additional_terrain: Optional[str]


class ObjectiveCardDict(DictModel):
    id: int
    name: str
    image_url: str


class PlayerDict(DictModel):
    id: int
    user_id: int
    field: str  # TODO: fill in
    left_player_id: int
    right_player_id: int
    score: int


class MonsterCardDict(DictModel):
    id: int
    name: str
    image_url: str
    shape_id: int
    exchange_order: str
