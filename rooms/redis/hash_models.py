from services.redis.base.models_base import HashModel


class RoomHash(HashModel):
    name: bytes
    password: bytes
    max_users: bytes
    admin_id: bytes
    user_ids: bytes
    is_game_started: bytes
    # is_ready_for_game: bytes
