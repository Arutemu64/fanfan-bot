from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

from fanfan.core.enums import UserRole

TicketId = NewType("TicketId", str)


@dataclass(frozen=True, slots=True)
class TicketModel:
    id: TicketId
    role: UserRole
    issued_by_id: UserId | None


from fanfan.core.models.user import UserId  # noqa: E402
