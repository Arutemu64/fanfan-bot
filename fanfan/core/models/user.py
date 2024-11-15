from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

from fanfan.core.enums import UserRole

UserId = NewType("UserId", int)


@dataclass(slots=True)
class UserModel:
    id: UserId
    username: str | None
    role: UserRole


@dataclass(slots=True)
class FullUserModel(UserModel):
    permissions: UserPermissionsModel
    settings: UserSettingsModel
    ticket: TicketModel | None


from fanfan.core.models.permissions import UserPermissionsModel  # noqa: E402
from fanfan.core.models.ticket import TicketModel  # noqa: E402
from fanfan.core.models.user_settings import UserSettingsModel  # noqa: E402
