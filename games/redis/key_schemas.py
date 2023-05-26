from services.redis.key_schemas_base import IKeySchema


class GameKeySchema(IKeySchema):
    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"game-tables:{id}"

    @property
    def ids_key(self) -> str:
        return "game-tables:ids"


class SeasonKeySchema(IKeySchema):
    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"seasons:{id}"

    @property
    def ids_key(self) -> str:
        return "seasons:ids"


class MoveKeySchema(IKeySchema):
    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"moves:{id}"

    @property
    def ids_key(self) -> str:
        return "moves:ids"


class PlayerKeySchema(IKeySchema):
    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"players:{id}"

    @property
    def ids_key(self) -> str:
        return "players:ids"


class MonsterCardKeySchema(IKeySchema):
    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"monster-cards:{id}"

    @property
    def ids_key(self) -> str:
        return "monster-cards:ids"
