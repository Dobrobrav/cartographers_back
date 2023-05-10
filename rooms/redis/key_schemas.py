from services.key_schemas_base import KeySchema


class RoomKeySchema(KeySchema):
    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"rooms:{id}"

    @staticmethod
    def get_ids_key() -> str:
        return "rooms:ids"
