from dataclasses import dataclass

from fanfan.core.vo.user import UserId, UserRole


@dataclass(frozen=True, slots=True, kw_only=True)
class UserDTO:
    id: UserId
    username: str | None
    first_name: str | None
    last_name: str | None
    role: UserRole
