from services.redis.key_schemas_base import IKeySchema


class RoomKeySchema(IKeySchema):
    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"rooms:{id}"

    @staticmethod
    def get_ids_key() -> str:
        return "rooms:ids"

    @staticmethod
    def get_user_id_room_id_index_key() -> str:
        return "room-id-user-id-index"

    @staticmethod
    def get_user_readiness_key(room_id: int,
                               user_id: int,
                               ) -> str:
        return f"rooms:{room_id}:users:{user_id}:is-ready"
