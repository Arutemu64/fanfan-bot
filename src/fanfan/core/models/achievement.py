from dataclasses import dataclass

from fanfan.core.vo.achievements import AchievementId, ReceivedAchievementId
from fanfan.core.vo.user import UserId


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
