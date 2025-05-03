from dataclasses import dataclass
from typing import NewType

from fanfan.core.models.user import UserId

FlagId = NewType("FlagId", int)


@dataclass(kw_only=True, slots=True)
class Flag:
    id: FlagId | None = None
    flag_name: str
    user_id: UserId
