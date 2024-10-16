from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

from fanfan.core.enums import UserRole

UserId = NewType("UserId", int)


@dataclass(frozen=True, slots=True)
class UserPermissionsModel:
    user_id: UserId
    can_send_feedback: bool


@dataclass(frozen=True, slots=True)
class UserSettingsModel:
    user_id: UserId
    items_per_page: int
    receive_all_announcements: bool


@dataclass(frozen=True, slots=True)
class UserModel:
    id: UserId
    username: str | None
    role: UserRole


@dataclass(frozen=True, slots=True)
class FullUserModel(UserModel):
    permissions: UserPermissionsModel
    settings: UserSettingsModel
    ticket: TicketModel | None


from fanfan.core.models.ticket import TicketModel  # noqa: E402
