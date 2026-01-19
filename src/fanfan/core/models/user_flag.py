from dataclasses import dataclass

from fanfan.core.vo.user import UserId
from fanfan.core.vo.user_flag import UserFlagId


@dataclass(kw_only=True, slots=True)
class UserFlag:
    id: UserFlagId | None = None
    name: str
    user_id: UserId
