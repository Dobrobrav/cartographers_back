from services.redis.key_schemas_base import IKeySchema


class GameKeySchema(IKeySchema):
    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"games:{id}"

    @property
    def ids_key(self) -> str:
        return "games:ids"

    @property
    def game_id_by_room_id_index_key(self) -> str:
        return "game-id-by-room-id-index"


class TerrainCardKeySchema(IKeySchema):
    @staticmethod
    def get_hash_key(id: int,
                     ) -> str:
        return f"terrain-cards:{id}"

    @property
    def ids_key(self) -> str:
        return "terrain-cards:ids"


class ObjectiveCardKeySchema(IKeySchema):

    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"objective-cards:{id}"

    @property
    def ids_key(self) -> str:
        return "objective-cards:ids"


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


class SeasonsScoreKeySchema(IKeySchema):

    @staticmethod
    def get_hash_key(id: int) -> str:
        return f'seasons_scores:{id}'

    @property
    def ids_key(self) -> str:
        return 'seasons_scores:ids'


class SeasonScoreKeySchema(IKeySchema):

    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"season_scores:{id}"

    @property
    def ids_key(self) -> str:
        return "season_scores:ids"


class MonsterCardKeySchema(IKeySchema):
    @staticmethod
    def get_hash_key(id: int) -> str:
        return f"monster-cards:{id}"

    @property
    def ids_key(self) -> str:
        return "monster-cards:ids"
