from dataclasses import dataclass
from enum import StrEnum

from fanfan.adapters.api.ticketscloud.dto.pagination import Pagination
from fanfan.adapters.api.ticketscloud.dto.ticket import Ticket


class OrderStatus(StrEnum):
    EXECUTED = "executed"
    DONE = "done"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass
class Order:
    id: str
    event: str
    status: OrderStatus
    tickets: list[Ticket]


@dataclass(slots=True, frozen=True)
class OrdersResponse:
    data: list[Order]
    pagination: Pagination
    total_count: int
