from __future__ import annotations

from dataclasses import dataclass

from fanfan.core.vo.ticket import TicketId
from fanfan.core.vo.user import UserId, UserRole


@dataclass(slots=True, kw_only=True)
class Ticket:
    id: TicketId
    role: UserRole
    used_by_id: UserId | None
    issued_by_id: UserId | None
