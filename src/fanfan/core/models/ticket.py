from __future__ import annotations

from dataclasses import dataclass

from fanfan.core.exceptions.tickets import TicketAlreadyUsed
from fanfan.core.vo.ticket import TicketId
from fanfan.core.vo.user import UserId, UserRole


@dataclass(slots=True, kw_only=True)
class Ticket:
    id: TicketId
    role: UserRole
    used_by_id: UserId | None
    issued_by_id: UserId | None

    def set_as_used(self, user_id: UserId):
        if self.used_by_id:
            raise TicketAlreadyUsed
        self.used_by_id = user_id
