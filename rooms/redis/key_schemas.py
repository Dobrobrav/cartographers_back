from services.redis.key_schemas_base import IKeySchema


class RoomKeySchema(IKeySchema):
    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"rooms:{id}"

    @property
    def ids_key(self) -> str:
        return "rooms:ids"

    @property
    def room_id_by_user_id_index_key(self):
        return "room-id-by-user-id-index"

    @property
    def model_id_by_model_name_index_key(self):
        return "room-id-by-room-name-index"

    @staticmethod
    def get_user_readiness_key(room_id: int,
                               user_id: int,
                               ) -> str:
        return f"rooms:{room_id}:users:{user_id}:is-ready"
