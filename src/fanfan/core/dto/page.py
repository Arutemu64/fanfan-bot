from dataclasses import dataclass
from typing import TypeVar

PageItem = TypeVar("PageItem")


@dataclass(kw_only=True, frozen=True, slots=True)
class Pagination:
    limit: int
    offset: int


@dataclass(frozen=True, slots=True)
class Page[PageItem]:
    items: list[PageItem]
    total: int
