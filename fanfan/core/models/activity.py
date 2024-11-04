from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

ActivityId = NewType("ActivityId", int)


@dataclass(slots=True)
class ActivityModel:
    id: ActivityId
    title: str
    description: str
    image_path: str | None
