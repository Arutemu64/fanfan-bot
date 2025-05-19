from dataclasses import dataclass

from fanfan.core.vo.user import UserId


@dataclass(frozen=True, slots=True)
class QuestPlayerDTO:
    user_id: UserId
    username: str | None
    points: int
    achievements_count: int
    rank: int | None


@dataclass(frozen=True, slots=True)
class QuestRatingDTO:
    players: list[QuestPlayerDTO]
    total: int
