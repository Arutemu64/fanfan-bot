from dataclasses import dataclass

from fanfan.core.vo.flag import FlagId
from fanfan.core.vo.user import UserId


@dataclass(kw_only=True, slots=True)
class Flag:
    id: FlagId | None = None
    name: str
    user_id: UserId
