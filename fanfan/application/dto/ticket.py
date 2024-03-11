from dataclasses import dataclass
from typing import Optional

from fanfan.common.enums import UserRole


@dataclass(frozen=True, slots=True)
class TicketDTO:
    id: str
    role: UserRole
    used_by_id: Optional[int]
    issued_by_id: Optional[int]
