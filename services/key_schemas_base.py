from abc import ABC, abstractmethod


class KeySchema(ABC):
    @staticmethod
    @abstractmethod
    def get_hash_key(id: int) -> str:
        pass

    @staticmethod
    @abstractmethod
    def get_ids_key() -> str:
        pass
    
    @staticmethod
    @abstractmethod
    def gen_id() -> int:
        pass
