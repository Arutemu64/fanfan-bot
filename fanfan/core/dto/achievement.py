from dataclasses import dataclass

from fanfan.core.models.achievement import AchievementId


@dataclass(slots=True, kw_only=True)
class AchievementUserDTO:
    id: AchievementId
    title: str
    description: str | None
    is_received: bool
