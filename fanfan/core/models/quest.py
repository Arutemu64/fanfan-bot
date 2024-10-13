from dataclasses import dataclass

from fanfan.core.models.ticket import TicketModel
from fanfan.core.models.user import UserId


@dataclass(frozen=True, slots=True)
class QuestParticipantDTO:
    id: UserId
    points: int
    achievements_count: int
    quest_registration: bool
    ticket: TicketModel | None
