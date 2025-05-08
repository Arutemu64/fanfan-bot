from dataclasses import dataclass

from fanfan.core.models.achievement import AchievementId
from fanfan.core.models.code import CodeId
from fanfan.core.models.ticket import TicketId
from fanfan.core.models.user import UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class CodeDTO:
    id: CodeId

    achievement_id: AchievementId | None
    user_id: UserId | None
    ticket_id: TicketId | None
