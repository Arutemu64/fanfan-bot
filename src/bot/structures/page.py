from typing import Generic, List, TypeVar

from pydantic import BaseModel, ConfigDict

AbstractModel = TypeVar("AbstractModel")


class Page(BaseModel, Generic[AbstractModel]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    items: List[AbstractModel]
    number: int
    total: int
