from abc import ABC, abstractmethod


class KeySchema(ABC):
    @abstractmethod
    def get_hash_key(self,
                     id: int,
                     ) -> str:
        pass

    @abstractmethod
    def get_ids_key(self) -> str:
        pass


class MonsterCardKeySchema(KeySchema):
    def get_hash_key(self,
                     id: int,
                     ) -> str:
        return f"monster-cards{id}"

    def get_ids_key(self) -> str:
        return "monster-cards:ids"
