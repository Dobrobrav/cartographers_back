from typing import MutableSequence, TypedDict, Optional

from games.common import SeasonName, URL, EShapeUnit
from services.redis.base.models_base import DictModel, PrettyModel


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
    terrain_card_ids: str
    monster_card_ids: str
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


class ShapeDict(DictModel):
    shape_value: str
    gives_coin: str  # 'true' or 'false' for json parser


class ObjectiveCardDict(DictModel):
    name: str
    text: str
    image_url: str


class PlayerDict(DictModel):
    user_id: int
    field: str
    left_player_id: int
    right_player_id: int
    coins: int
    seasons_score_id: int
    finished_move: str  # true or false


class PlayerPretty(PrettyModel):
    id: int
    name: str
    score: int
    # image: URL - for the future


class SeasonsScoreDict(DictModel):
    spring_score_id: int
    summer_score_id: int
    fall_score_id: int
    winter_score_id: int
    coins: int
    total: int


class SeasonScoreDict(DictModel):
    from_first_task: int
    from_second_task: int
    from_coins: int
    monsters: int
    total: int


class MonsterCardDict(DictModel):
    name: str
    image_url: str
    shape_id: int
    exchange_order: str


class GamePretty(TypedDict):
    id: int
    room_name: str
    player_field: MutableSequence[MutableSequence[int]]
    seasons: dict[SeasonName, URL]
    # tasks: MutableSequence['TaskPretty']
    current_season_name: str
    players: MutableSequence['PlayerPretty']
    discovery_card: 'DiscoveryCardPretty'
    is_prev_card_ruins: bool
    player_coins: int
    player_score: int
    season_scores: 'SeasonsScorePretty'


class DiscoveryCardPretty(TypedDict):
    image: str
    is_anomaly: bool
    terrain_int: int
    additional_terrain_int: Optional[int]
    shape: 'ShapePretty'
    additional_shape: Optional['ShapePretty']


class ShapePretty(TypedDict):
    gives_coin: bool
    shape_value: MutableSequence[MutableSequence[EShapeUnit]]


class SeasonScorePrettyGen(TypedDict):
    from_coins: int
    monsters: int
    total: int


class SeasonScorePretty(TypedDict):
    from_coins: int
    monsters: int
    total: int
    from_first_task: int
    from_second_task: int


class SpringScorePretty(SeasonScorePrettyGen):
    A: int
    B: int


class SummerScorePretty(SeasonScorePrettyGen):
    B: int
    C: int


class FallScorePretty(SeasonScorePrettyGen):
    C: int
    D: int


class WinterScorePretty(SeasonScorePrettyGen):
    D: int
    A: int


class SeasonsScorePretty(PrettyModel):
    spring_score: SeasonScorePretty
    summer_score: SeasonScorePretty
    fall_score: SeasonScorePretty
    winter_score: SeasonScorePretty


class TaskPretty(PrettyModel):
    text: str
    image: str
