from dataclasses import dataclass

from fanfan.core.vo.achievements import AchievementId


@dataclass(slots=True, kw_only=True)
class AchievementUserDTO:
    id: AchievementId
    title: str
    description: str | None
    is_received: bool
