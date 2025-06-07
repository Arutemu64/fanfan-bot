from __future__ import annotations

import enum
from typing import NewType

UserId = NewType("UserId", int)


class UserRole(enum.StrEnum):
    VISITOR = ("visitor", "Зритель", "Зрители")
    PARTICIPANT = ("participant", "Участник", "Участники")
    HELPER = ("helper", "Волонтёр", "Волонтёры")
    ORG = ("org", "Организатор", "Организаторы")

    def __new__(cls, value, label, label_plural):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        obj.label_plural = label_plural
        return obj

    def __str__(self):
        return self.label
