from typing import Optional

from pydantic import BaseModel, ConfigDict


class AchievementDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: int
    title: str
    description: Optional[str]


class ReceivedAchievementDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    user_id: int
    achievement_id: int


class FullAchievementDTO(AchievementDTO):
    user_received: Optional[ReceivedAchievementDTO]
