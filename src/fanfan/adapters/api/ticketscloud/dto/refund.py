from dataclasses import dataclass
from enum import StrEnum

from fanfan.adapters.api.ticketscloud.dto.pagination import Pagination
from fanfan.adapters.api.ticketscloud.dto.ticket import Ticket


class RefundStatus(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class Refund:
    id: str
    event: str
    status: RefundStatus
    tickets: list[Ticket]


@dataclass(slots=True, frozen=True)
class RefundsResponse:
    data: list[Refund]
    pagination: Pagination
    total_count: int
