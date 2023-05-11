from abc import ABC, abstractmethod


class IKeySchema(ABC):
    @staticmethod
    @abstractmethod
    def get_hash_key(id: int) -> str:
        pass

    @staticmethod
    @abstractmethod
    def get_ids_key() -> str:
        pass
