from dataclasses import dataclass
from typing import Optional

from fastapi_storages import StorageImage


@dataclass
class ActivityDTO:
    id: int
    title: str
    description: str
    subtext: Optional[str]
    image: Optional[StorageImage]
