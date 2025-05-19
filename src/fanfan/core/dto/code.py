from dataclasses import dataclass

from fanfan.core.vo.achievements import AchievementId
from fanfan.core.vo.code import CodeId
from fanfan.core.vo.ticket import TicketId
from fanfan.core.vo.user import UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class CodeDTO:
    id: CodeId

    achievement_id: AchievementId | None
    user_id: UserId | None
    ticket_id: TicketId | None
