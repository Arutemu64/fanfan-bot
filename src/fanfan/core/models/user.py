from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fanfan.core.vo.telegram import TelegramUserId
from fanfan.core.vo.user import UserId, Username, UserRole


@dataclass(slots=True, kw_only=True)
class UserSettings:
    items_per_page: int = 4
    receive_all_announcements: bool = True


@dataclass(slots=True, kw_only=True)
class User:  # noqa: PLW1641
    id: UserId | None = None

    username: Username | None
    tg_id: TelegramUserId | None

    first_name: str | None
    last_name: str | None

    role: UserRole
    settings: UserSettings

    def set_role(self, role: UserRole):
        self.role = role

    def __eq__(self, other: User | Any) -> bool:
        return isinstance(other, User) and self.id == other.id
