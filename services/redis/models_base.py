from abc import ABC
from dataclasses import dataclass
from typing import TypedDict, TypeVar

T = TypeVar('T')


@dataclass
class DataClassModel(ABC):
    id: int


class DictModel(TypedDict):
    id: int


class HashModel(TypedDict):
    id: bytes


def get_enum_by_value(cls: type[T],
                      value: str | int,
                      ) -> T:
    type = cls.__new__(cls, value)
    return type
