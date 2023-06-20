from abc import ABC
from dataclasses import dataclass
from typing import TypedDict, TypeVar



@dataclass
class DataClassModel(ABC):
    id: int


class DictModel(TypedDict):
    id: int


class HashModel(TypedDict):
    id: bytes


class PrettyModel(TypedDict):
    pass


