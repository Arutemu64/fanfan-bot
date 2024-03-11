from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class AchievementDTO:
    id: int
    title: str
    description: Optional[str]


@dataclass(frozen=True, slots=True)
class ReceivedAchievementDTO:
    user_id: int
    achievement_id: int


@dataclass(frozen=True, slots=True)
class FullAchievementDTO(AchievementDTO):
    user_received: Optional[ReceivedAchievementDTO]
