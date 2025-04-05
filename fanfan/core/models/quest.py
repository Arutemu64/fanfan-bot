from dataclasses import dataclass

from fanfan.core.models.user import UserId


@dataclass(slots=True, kw_only=True)
class QuestParticipant:
    id: UserId
    points: int

    def add_points(self, points: int) -> None:
        self.points += points


@dataclass(slots=True, kw_only=True)
class QuestParticipantFull(QuestParticipant):
    achievements_count: int
