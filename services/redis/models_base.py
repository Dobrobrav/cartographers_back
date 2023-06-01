from abc import ABC
from dataclasses import dataclass
from typing import TypedDict


@dataclass
class DataClassModel(ABC):
    id: int


class DictModel(TypedDict):
    id: int


