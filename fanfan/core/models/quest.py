from dataclasses import dataclass

from fanfan.core.models.user import UserId


@dataclass(slots=True)
class QuestParticipantModel:
    id: UserId
    points: int

    def add_points(self, points: int) -> None:
        self.points += points


@dataclass(slots=True)
class FullQuestParticipantModel(QuestParticipantModel):
    achievements_count: int
    quest_registration: bool
