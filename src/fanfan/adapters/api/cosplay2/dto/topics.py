from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Topic:
    id: int
    card_code: str
    title: str
