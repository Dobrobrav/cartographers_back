from services.redis.key_schemas_base import IKeySchema


class MonsterCardKeySchema(IKeySchema):
    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"monster-cards:{id}"

    @staticmethod
    def get_ids_key() -> str:
        return "monster-cards:ids"


class GameTableKeySchema(IKeySchema):
    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"game-tables:{id}"

    @staticmethod
    def get_ids_key() -> str:
        return "game-tables:ids"


class SeasonKeySchema(IKeySchema):
    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"seasons:{id}"

    @staticmethod
    def get_ids_key() -> str:
        return "seasons:ids"


class MoveKeySchema(IKeySchema):
    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"moves:{id}"

    @staticmethod
    def get_ids_key() -> str:
        return "moves:ids"


class PlayerRedis(IKeySchema):
    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"players:{id}"

    @staticmethod
    def get_ids_key() -> str:
        return "players:ids"
