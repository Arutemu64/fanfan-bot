import enum
from dataclasses import dataclass
from typing import Generic, Sequence, TypeVar

AbstractModel = TypeVar("AbstractModel")


@dataclass
class Page(Generic[AbstractModel]):
    items: Sequence[AbstractModel]
    number: int
    total: int


@dataclass
class Notification:
    user_id: int
    text: str


class UserRole(enum.IntEnum):
    def __new__(cls, value, label, label_plural):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        obj.label_plural = label_plural
        return obj

    VISITOR = (0, "Зритель", "Зрители")
    HELPER = (1, "Волонтёр", "Волонтёры")
    ORG = (2, "Организатор", "Организаторы")
