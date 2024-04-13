from typing import Optional

from pydantic import BaseModel, ConfigDict

from fanfan.application.dto.ticket import TicketDTO
from fanfan.common.enums import UserRole


class CreateUserDTO(BaseModel):
    id: int
    username: Optional[str] = None
    role: Optional[UserRole] = None


class UserDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: int
    username: Optional[str]
    role: UserRole


class UserPermissionsDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    can_send_feedback: bool


class UserSettingsDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    items_per_page: int
    receive_all_announcements: bool


class FullUserDTO(UserDTO):
    permissions: UserPermissionsDTO
    settings: UserSettingsDTO
    ticket: Optional[TicketDTO]


class UpdateUserDTO(BaseModel):
    id: int
    username: Optional[str] = ""
    role: Optional[UserRole] = None


class UpdateUserSettingsDTO(BaseModel):
    user_id: int
    items_per_page: Optional[int] = None
    receive_all_announcements: Optional[bool] = None


class UserStats(BaseModel):
    user_id: int
    achievements_count: int
    total_achievements: int
