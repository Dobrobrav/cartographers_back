from typing import MutableSequence, TypedDict, TypeAlias, Literal, Optional

from services.redis.models_base import DictModel

SeasonName: TypeAlias = str
URL: TypeAlias = str
UserID: TypeAlias = int
ScoreSource: TypeAlias = str
ScoreValue: TypeAlias = int


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


class ShapeDict(DictModel):
    shape_value: str
    gives_coin: str  # 'true' or 'false' for json parser


class ObjectiveCardDict(DictModel):
    name: str
    image_url: str


class PlayerDict(DictModel):
    user_id: int
    field: str
    left_player_id: int
    right_player_id: int
    coins: int
    seasons_score_id: int


class PlayerPretty(TypedDict):
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


# create dc as well and the transformers. or it's not necessary
# create a dict str -> int for Hablak
class GamePretty(TypedDict):
    id: int
    room_name: str
    player_field: MutableSequence[MutableSequence[int]]
    seasons: dict[SeasonName, URL]
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
    is_prev_card_ruins: bool


class ShapePretty(TypedDict):
    gives_coin: bool
    shape_value: MutableSequence[MutableSequence[Literal[1, 0]]]


class SeasonScorePretty(TypedDict):
    from_coins: int
    monsters: int
    total: int


class SpringScorePretty(SeasonScorePretty):
    A: int
    B: int


class SummerScorePretty(SeasonScorePretty):
    B: int
    C: int


class FallScorePretty(SeasonScorePretty):
    C: int
    D: int


class WinterScorePretty(SeasonScorePretty):
    D: int
    A: int


class SeasonsScorePretty(TypedDict):
    spring_score: SpringScorePretty
    summer_score: SummerScorePretty
    fall_score: FallScorePretty
    winter_score: WinterScorePretty
    # coins: int
    # total: int
