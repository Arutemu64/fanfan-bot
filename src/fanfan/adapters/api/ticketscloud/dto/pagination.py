from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Pagination:
    page: int
    page_size: int
    total: int
