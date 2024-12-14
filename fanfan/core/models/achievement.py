from dataclasses import dataclass
from typing import NewType

AchievementId = NewType("AchievementId", int)
SecretId = NewType("SecretId", str)


@dataclass(slots=True, kw_only=True)
class Achievement:
    id: AchievementId
    title: str
    description: str | None


@dataclass(slots=True, kw_only=True)
class FullAchievement(Achievement):
    received: bool
