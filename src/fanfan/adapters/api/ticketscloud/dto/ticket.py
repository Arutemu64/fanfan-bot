from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Ticket:
    id: str
    serial: str
    number: int
    barcode: str | None
    status: str
    price: str
    nominal: str
    discount: str
    extra: str
    full: str
    set: str
    tariff: str | None
