from dataclasses import dataclass
from enum import StrEnum

from fanfan.adapters.api.ticketscloud.dto.pagination import Pagination
from fanfan.adapters.api.ticketscloud.dto.ticket import Ticket


class OrderStatus(StrEnum):
    EXECUTED = "executed"
    DONE = "done"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    IN_PROGRESS = "in_progress"


@dataclass
class Order:
    id: str
    status: OrderStatus
    event: str
    tickets: list[Ticket]


@dataclass(slots=True, frozen=True)
class OrdersResponse:
    data: list[Order]
    pagination: Pagination
    total_count: int
