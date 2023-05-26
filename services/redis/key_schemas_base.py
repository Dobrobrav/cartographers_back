from abc import ABC, abstractmethod


class IKeySchema(ABC):
    @staticmethod
    @abstractmethod
    def get_hash_key(id: int) -> str:
        pass

    @property
    @abstractmethod
    def ids_key(self) -> str:
        pass
