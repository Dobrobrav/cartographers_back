from typing import TypeVar

T = TypeVar('T')


def get_enum_by_value(cls: type[T],
                      value: str | int,
                      ) -> T:
    type = cls.__new__(cls, value)
    return type
