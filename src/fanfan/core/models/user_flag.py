from dataclasses import dataclass

from fanfan.core.vo.user_flag import UserFlagId
from fanfan.core.vo.user import UserId


@dataclass(kw_only=True, slots=True)
class UserFlag:
    id: UserFlagId | None = None
    name: str
    user_id: UserId
