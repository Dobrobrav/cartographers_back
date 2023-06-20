from services.redis.base.key_schemas_base import IKeySchema


class RoomKeySchema(IKeySchema):
    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"rooms:{id}"

    @property
    def ids_key(self) -> str:
        return "rooms:ids"

    @property
    def room_id_by_user_id_index_key(self):
        return "room_id_by_user_id_index"

    @property
    def model_id_by_model_name_index_key(self):
        return "room_id_by_room_name_index"

    @staticmethod
    def user_readiness_key(room_id: int,
                           user_id: int,
                           ) -> str:
        return f"rooms:{room_id}_user_{user_id}_is_ready"
