from dataclasses import dataclass
from typing import NewType

AchievementId = NewType("AchievementId", int)


@dataclass(slots=True, kw_only=True)
class Achievement:
    id: AchievementId
    title: str
    description: str | None
