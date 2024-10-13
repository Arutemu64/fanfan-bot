from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

ActivityId = NewType("ActivityId", int)


@dataclass(frozen=True, slots=True)
class ActivityModel:
    id: ActivityId
    title: str
    description: str
    subtext: str | None
    image_path: str | None
