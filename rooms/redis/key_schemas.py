from services.redis.key_schemas_base import IKeySchema


class RoomKeySchema(IKeySchema):
    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"rooms:{id}"

    @staticmethod
    def get_ids_key() -> str:
        return "rooms:ids"
