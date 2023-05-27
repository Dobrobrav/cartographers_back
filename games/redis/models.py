from dataclasses import dataclass, field

from games.models import EFieldTerrainType, ECardTerrainType, ETerrainCardType
from games.redis.dao import EDiscoveryCardType, ESeasonName
from services.redis.redis_models_base import RedisModel


@dataclass
class GameRedis(RedisModel):
    id: int
    lobby_id: int
    monster_card_ids_pull: set[int]
    terrain_card_ids_pull: set[int]
    season_ids_pull: set[int]
    current_move_id: int | None
    admin_id: int
    player_ids: list[int]


@dataclass
class SeasonRedis(RedisModel):
    id: int
    name: ESeasonName
    ending_points: int
    objective_card_ids: set[int]
    terrain_card_ids: set[int]  # make sure it's a copy of set
    monster_card_ids: set[int]  # same as above
    current_move_id: int | None


@dataclass
class MoveRedis(RedisModel):
    id: int
    season_card_id: int
    is_prev_card_ruins: bool
    discovery_card_type: EDiscoveryCardType
    discovery_card_id: int
    season_points: int


@dataclass
class TerrainCardRedis(RedisModel):
    id: int
    name: str
    image_url: str
    card_type: ETerrainCardType
    shape: str
    terrain: ECardTerrainType
    season_points: int
    additional_shape: str | None = None
    additional_terrain: ECardTerrainType | None = None


@dataclass
class PlayerRedis(RedisModel):
    id: int
    user_id: int
    field: list[list[EFieldTerrainType]]
    left_player_id: int
    right_player_id: int
    score: int


@dataclass
class MonsterCardRedis(RedisModel):
    id: int
    name: str
    image_url: str
    shape: str
    exchange_order: str
