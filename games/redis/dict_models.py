from typing import MutableSequence, Optional, TypedDict, TypeAlias, Literal

from games.models import ETerrainCardType, ETerrainTypeLimited, ETerrainTypeAll, EExchangeOrder
from games.redis.dc_models import ESeasonName, EDiscoveryCardType
from services.redis.models_base import DictModel

SeasonName: TypeAlias = str
URL: TypeAlias = str
UserID: TypeAlias = int
Score: TypeAlias = int
ScoreSource: TypeAlias = str
ScoreValue: TypeAlias = int


# TODO: I can't put None into dict for redis
class GameDict(DictModel):
    room_id: int
    admin_id: int
    player_ids: str
    monster_card_ids: str
    terrain_card_ids: str
    season_ids: str
    current_season_id: int


class SeasonDict(DictModel):
    name: str
    image_url: str
    points_to_end: int
    objective_card_ids: str
    terrain_card_ids: str  # make sure it's a copy of set
    monster_card_ids: str  # same as above
    current_move_id: int


class MoveDict(DictModel):
    is_prev_card_ruins: int
    discovery_card_type: str
    discovery_card_id: int
    season_points: int


class TerrainCardDict(DictModel):
    name: str
    image_url: str
    card_type: str
    shape_id: int | str  # str for cases when attr is absent
    terrain: str
    season_points: int | str
    additional_shape_id: int | str
    additional_terrain: str


class ObjectiveCardDict(DictModel):
    name: str
    image_url: str


class PlayerDict(DictModel):
    user_id: int
    field: str  # TODO: fill in
    left_player_id: int
    right_player_id: int
    score: int


class MonsterCardDict(DictModel):
    name: str
    image_url: str
    shape_id: int
    exchange_order: str


# create dc as well and the transformers. or it's not necessary
# create a dict str -> int for Hablak
class GameDictPretty(TypedDict):
    id: int
    room_name: str
    player_field: MutableSequence[MutableSequence[int]]
    seasons: dict[SeasonName, URL]
    current_season_name: str
    players: MutableSequence['PlayerDictPretty']
    discovery_card: dict[str, str | MutableSequence[MutableSequence[int]]]
    is_prev_card_ruins: bool
    player_coins: int
    player_score: int
    season_score: dict[SeasonName, dict[ScoreSource, ScoreValue]]


class PlayerDictPretty(TypedDict):
    id: int
    name: str
    score: int
    # image: URL - for the future

