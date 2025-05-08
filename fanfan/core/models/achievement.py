from dataclasses import dataclass
from typing import NewType

from fanfan.core.models.user import UserId

AchievementId = NewType("AchievementId", int)
ReceivedAchievementId = NewType("ReceivedAchievementId", int)


@dataclass(slots=True, kw_only=True)
class Achievement:
    id: AchievementId
    title: str
    description: str | None


@dataclass(slots=True, kw_only=True)
class ReceivedAchievement:
    id: ReceivedAchievementId | None = None
    achievement_id: AchievementId
    user_id: UserId
