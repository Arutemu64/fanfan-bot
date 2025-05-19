from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class TicketTypeResponse:
    name: str


@dataclass(slots=True, frozen=True)
class TicketResponse:
    number: str
    ticket_type: TicketTypeResponse
