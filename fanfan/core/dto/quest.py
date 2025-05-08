from dataclasses import dataclass

from fanfan.core.models.user import UserId


@dataclass(frozen=True, slots=True)
class QuestPlayerDTO:
    user_id: UserId
    username: str
    points: int
    achievements_count: int
    rank: int
