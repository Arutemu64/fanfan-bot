from dataclasses import dataclass

from fanfan.core.models.ticket import Ticket
from fanfan.core.models.user import UserSettings
from fanfan.core.vo.permission import (
    PermissionName,
    PermissionObjectId,
    PermissionObjectType,
)
from fanfan.core.vo.telegram import TelegramUserId
from fanfan.core.vo.user import UserId, UserRole


@dataclass(frozen=True, slots=True, kw_only=True)
class UserDTO:
    id: UserId
    tg_id: TelegramUserId | None
    username: str | None
    first_name: str | None
    last_name: str | None
    role: UserRole


@dataclass(frozen=True, slots=True, kw_only=True)
class UserPermissionDTO:
    name: PermissionName
    object_type: PermissionObjectType | None
    object_id: PermissionObjectId | None


@dataclass(frozen=True, slots=True, kw_only=True)
class FullUserDTO(UserDTO):
    settings: UserSettings
    ticket: Ticket | None
    permissions: list[UserPermissionDTO]

    def check_permission(self, perm_name: PermissionName) -> bool:
        return any(p.name == perm_name for p in self.permissions)
