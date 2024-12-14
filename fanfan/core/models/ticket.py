from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

TicketId = NewType("TicketId", str)


@dataclass(slots=True, kw_only=True)
class Ticket:
    id: TicketId
    role: UserRole
    used_by_id: UserId | None
    issued_by_id: UserId | None


from fanfan.core.models.user import UserId, UserRole  # noqa: E402
