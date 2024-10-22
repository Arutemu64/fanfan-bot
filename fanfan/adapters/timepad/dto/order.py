import enum
from dataclasses import dataclass

from fanfan.adapters.timepad.dto.ticket import TicketResponse

# https://dev.timepad.ru/api/get-v1-events-event-id-orders/


class OrderStatus(enum.StrEnum):
    # https://dev.timepad.ru/api/hooks/#spisok-vozmozhnyh-statusov-biletov
    NOT_PAID = "notpaid"
    OK = "ok"
    PAID = "paid"
    INACTIVE = "inactive"
    DELETED = "deleted"
    BLOCKED = "blocked"
    RETURNED = "returned"
    BOOKED = "booked"
    PENDING = "pending"
    REJECTED = "rejected"
    BOOKED_OFFLINE = "booked_offline"
    PAID_OFFLINE = "paid_offline"
    PAID_UR = "paid_ur"
    TRANSFER_PAYMENT = "transfer_payment"
    RETURN_PAYMENT_REQUEST = "return_payment_request"
    RETURN_PAYMENT_REJECT = "return_payment_reject"
    RETURN_ORG = "return_org"
    RETURN_TP = "return_tp"


@dataclass(slots=True, frozen=True)
class OrderStatusResponse:
    name: OrderStatus
    title: str


@dataclass(slots=True, frozen=True)
class OrderEventResponse:
    id: int


@dataclass(slots=True, frozen=True)
class RegistrationOrderResponse:
    id: int
    status: OrderStatusResponse
    tickets: list[TicketResponse]
    event: OrderEventResponse | None = None


@dataclass(slots=True, frozen=True)
class RegistrationOrdersResponse:
    total: int
    values: list[RegistrationOrderResponse]
