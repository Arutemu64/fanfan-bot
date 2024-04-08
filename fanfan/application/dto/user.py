from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

from fanfan.application.dto.ticket import TicketDTO
from fanfan.common.enums import UserRole


class CreateUserDTO(BaseModel):
    id: int
    username: Optional[str] = None
    role: Optional[UserRole] = None


@dataclass(frozen=True, slots=True)
class UserDTO:
    id: int
    username: Optional[str]
    role: UserRole
    items_per_page: int
    receive_all_announcements: bool


@dataclass(frozen=True, slots=True)
class FullUserDTO(UserDTO):
    ticket: Optional[TicketDTO]


class UpdateUserDTO(BaseModel):
    id: int
    username: Optional[str] = ""
    role: Optional[UserRole] = None
    items_per_page: Optional[int] = None
    receive_all_announcements: Optional[bool] = None


@dataclass(frozen=True, slots=True)
class UserStats:
    user_id: int
    achievements_count: int
    total_achievements: int
