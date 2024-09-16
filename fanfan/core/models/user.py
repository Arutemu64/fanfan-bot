from __future__ import annotations

from dataclasses import dataclass

from fanfan.core.enums import UserRole


@dataclass(frozen=True, slots=True)
class UserDTO:
    id: int
    username: str | None
    role: UserRole


@dataclass(frozen=True, slots=True)
class UserPermissionsDTO:
    can_send_feedback: bool


@dataclass(frozen=True, slots=True)
class UserSettingsDTO:
    items_per_page: int
    receive_all_announcements: bool


@dataclass(frozen=True, slots=True)
class FullUserDTO(UserDTO):
    permissions: UserPermissionsDTO
    settings: UserSettingsDTO
    ticket: TicketDTO | None


@dataclass(frozen=True, slots=True)
class UserStats:
    user_id: int
    achievements_count: int
    total_achievements: int


from fanfan.core.models.ticket import TicketDTO  # noqa: E402
