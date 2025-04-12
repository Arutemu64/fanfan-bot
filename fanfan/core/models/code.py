from dataclasses import dataclass
from typing import NewType

from fanfan.core.models.achievement import AchievementId
from fanfan.core.models.ticket import TicketId
from fanfan.core.models.user import UserId

CodeId = NewType("CodeId", str)


@dataclass(slots=True, kw_only=True)
class Code:
    id: CodeId

    achievement_id: AchievementId | None
    user_id: UserId | None
    ticket_id: TicketId | None
