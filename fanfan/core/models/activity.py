from dataclasses import dataclass
from pathlib import Path
from typing import NewType

ActivityId = NewType("ActivityId", int)


@dataclass(slots=True, kw_only=True)
class Activity:
    id: ActivityId
    title: str
    description: str
    image_path: Path | None
