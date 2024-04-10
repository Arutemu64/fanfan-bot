from dataclasses import dataclass
from typing import Generic, List, TypeVar

PageItem = TypeVar("PageItem")


@dataclass(frozen=True, slots=True)
class Page(Generic[PageItem]):
    items: List[PageItem]
    number: int
    total_pages: int
