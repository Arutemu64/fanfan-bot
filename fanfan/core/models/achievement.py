from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AchievementDTO:
    id: int
    title: str
    description: str | None


@dataclass(frozen=True, slots=True)
class UserAchievementDTO(AchievementDTO):
    received: bool
