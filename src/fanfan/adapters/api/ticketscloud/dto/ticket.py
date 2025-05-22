from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Ticket:
    barcode: str
    discount: float
    extra: float
    full: float
    id: str
    nominal: float
    number: int
    price: float
    serial: str
    set: str
    status: str
