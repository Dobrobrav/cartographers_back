from services.redis.key_schemas_base import IKeySchema


class UserKeySchema(IKeySchema):
    @staticmethod
    def get_hash_key(id: int,
                     ) -> str:
        pass

    @property
    def ids_key(self) -> str:
        pass
