from dataclasses import dataclass
from typing import NewType

from fanfan.core.models.user import UserId

ContestEntryId = NewType("ContestEntryId", int)


@dataclass(kw_only=True, slots=True)
class ContestEntry:
    id: ContestEntryId | None = None
    contest_name: str
    user_id: UserId
