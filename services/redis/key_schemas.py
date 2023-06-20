from services.redis.base.key_schemas_base import IKeySchema


class UserKeySchema(IKeySchema):
    @staticmethod
    def get_hash_key(id: int,
                     ) -> str:
        return f"users:{id}"

    @property
    def ids_key(self) -> str:
        return "users:ids"
