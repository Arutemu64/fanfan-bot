from dataclasses import dataclass
from typing import Generic, List, TypeVar

AbstractModel = TypeVar("AbstractModel")


@dataclass
class Page(Generic[AbstractModel]):
    items: List[AbstractModel]
    number: int
    total: int
