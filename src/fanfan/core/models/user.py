from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fanfan.core.models.ticket import Ticket
from fanfan.core.vo.user import UserId, UserRole


@dataclass(slots=True, kw_only=True)
class UserSettings:
    items_per_page: int = 5
    receive_all_announcements: bool = True


@dataclass(slots=True, kw_only=True)
class User:  # noqa: PLW1641
    id: UserId
    username: str | None
    first_name: str | None
    last_name: str | None
    role: UserRole

    settings: UserSettings

    def set_role(self, role: UserRole):
        self.role = role

    def __eq__(self, other: User | Any) -> bool:
        return isinstance(other, User) and self.id == other.id


@dataclass(slots=True, kw_only=True)
class UserData(User):
    ticket: Ticket | None
