from services.redis.base.models_base import HashModel


class GameHash(HashModel):
    room_id: bytes
    admin_id: bytes
    player_ids: bytes
    monster_card_ids: bytes
    terrain_card_ids: bytes
    season_ids: bytes
    current_season_id: bytes
    last_season_id: bytes
    is_finished: bytes


class SeasonHash(HashModel):
    name: bytes
    image_url: bytes
    current_points: bytes
    max_points: bytes
    objective_card_ids: bytes
    terrain_card_ids: bytes
    monster_card_ids: bytes
    current_move_id: bytes
    is_finished: bytes


class MoveHash(HashModel):
    is_on_ruins: bytes
    discovery_card_type: bytes
    discovery_card_id: bytes


class TerrainCardHash(HashModel):
    name: bytes
    image_url: bytes
    card_type: bytes
    shape_id: bytes
    terrain: bytes
    season_points: bytes
    additional_shape_id: bytes
    additional_terrain: bytes


class ShapeHash(HashModel):
    shape_value: bytes
    gives_coin: bytes


class ObjectiveCardHash(HashModel):
    name: bytes
    text: bytes
    image_url: bytes


class PlayerHash(HashModel):
    user_id: bytes  # not a substitute of id, it's another attr
    field: bytes
    clockwise_player_id: bytes
    counterclockwise_player_id: bytes
    coins: bytes
    seasons_score_id: bytes
    is_move_finished: bytes


class SeasonsScoreHash(HashModel):
    spring_score_id: bytes
    summer_score_id: bytes
    fall_score_id: bytes
    winter_score_id: bytes
    coins: bytes
    total: bytes


class SeasonScoreHash(HashModel):
    from_first_task: bytes
    from_second_task: bytes
    from_coins: bytes
    monsters: bytes
    total: bytes


class MonsterCardHash(HashModel):
    name: bytes
    image_url: bytes
    shape_id: bytes
    exchange_order: bytes
