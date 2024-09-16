from dataclasses import dataclass

from fanfan.core.enums import UserRole


@dataclass(frozen=True, slots=True)
class TicketDTO:
    id: str
    role: UserRole
    used_by_id: int | None
    issued_by_id: int | None
