import enum
from dataclasses import dataclass


class OrderStatus(enum.StrEnum):
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


@dataclass
class TicketTypeResponse:
    name: str


@dataclass
class TicketResponse:
    number: str
    ticket_type: TicketTypeResponse


@dataclass
class OrderStatusResponse:
    name: OrderStatus
    title: str


@dataclass
class RegistrationOrderResponse:
    status: OrderStatusResponse
    tickets: list[TicketResponse]


@dataclass
class RegistrationOrdersResponse:
    total: int
    values: list[RegistrationOrderResponse]
