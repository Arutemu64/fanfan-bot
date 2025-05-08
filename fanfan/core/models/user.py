from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Any, NewType

UserId = NewType("UserId", int)


class UserRole(enum.StrEnum):
    VISITOR = (enum.auto(), "Зритель", "Зрители")
    PARTICIPANT = (enum.auto(), "Участник", "Участники")
    HELPER = (enum.auto(), "Волонтёр", "Волонтёры")
    ORG = (enum.auto(), "Организатор", "Организаторы")

    def __new__(cls, value, label, label_plural):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        obj.label_plural = label_plural
        return obj

    def __str__(self):
        return self.label


@dataclass(slots=True, kw_only=True)
class User:
    id: UserId
    username: str | None
    first_name: str | None
    last_name: str | None
    role: UserRole

    permissions: UserPermissions
    settings: UserSettings

    def __eq__(self, other: User | Any) -> bool:
        return bool(isinstance(other, User) and self.id == other.id)


@dataclass(slots=True, kw_only=True)
class UserData(User):
    ticket: Ticket | None


from fanfan.core.models.permissions import UserPermissions  # noqa: E402
from fanfan.core.models.ticket import Ticket  # noqa: E402
from fanfan.core.models.user_settings import UserSettings  # noqa: E402
