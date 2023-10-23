import enum
from dataclasses import dataclass
from typing import Generic, List, TypeVar

AbstractModel = TypeVar("AbstractModel")


@dataclass
class Page(Generic[AbstractModel]):
    items: List[AbstractModel]
    number: int
    total: int


@dataclass
class Notification:
    user_id: int
    text: str


class UserRole(enum.IntEnum):
    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    VISITOR = (0, "Зритель")
    HELPER = (1, "Волонтёр")
    ORG = (2, "Организатор")
