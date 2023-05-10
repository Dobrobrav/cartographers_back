from services.key_schemas_base import KeySchema


class MonsterCardKeySchema(KeySchema):
    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"monster-cards:{id}"

    @staticmethod
    def get_ids_key() -> str:
        return "monster-cards:ids"

    @staticmethod
    def gen_id() -> int:
        pass
