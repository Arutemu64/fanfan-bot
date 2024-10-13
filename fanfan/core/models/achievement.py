from dataclasses import dataclass
from typing import NewType

AchievementId = NewType("AchievementId", int)
SecretId = NewType("SecretId", str)


@dataclass(frozen=True, slots=True)
class AchievementModel:
    id: AchievementId
    title: str
    description: str | None


@dataclass(frozen=True, slots=True)
class FullAchievementModel(AchievementModel):
    received: bool
