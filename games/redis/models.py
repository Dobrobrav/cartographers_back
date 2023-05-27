from dataclasses import dataclass

from games.models import EFieldTerrain
from services.redis.redis_models_base import RedisModel


@dataclass
class GameRedis(RedisModel):
    id: int
    lobby_id: int
    monster_card_for_game_ids: list[int]
    discovery_card_for_game_ids: list[int]
    season_for_game_ids: list[int]
    current_move_id: int
    admin_id: int
    player_ids: list[int]


@dataclass
class SeasonRedis(RedisModel):
    id: int
    points_to_end_season: int
    objective_card_ids: list[int]


@dataclass
class MoveRedis(RedisModel):
    id: int
    is_prev_card_ruins: bool
    discovery_card_points_collected: int
    current_card_id: int  # can be either monster_card or discovery_card


@dataclass
class PlayerRedis(RedisModel):
    id: int
    user_id: int
    field: list[list[EFieldTerrain]]
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
