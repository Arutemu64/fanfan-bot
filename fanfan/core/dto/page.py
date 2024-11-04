from dataclasses import dataclass
from typing import Generic, TypeVar

PageItem = TypeVar("PageItem")


@dataclass(kw_only=True, frozen=True, slots=True)
class Pagination:
    limit: int
    offset: int


@dataclass(frozen=True, slots=True)
class Page(Generic[PageItem]):
    items: list[PageItem]
    total: int
