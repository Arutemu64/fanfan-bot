from dataclasses import dataclass
from pathlib import Path

from fanfan.core.models.activity import ActivityId


@dataclass(frozen=True, slots=True, kw_only=True)
class ActivityDTO:
    id: ActivityId
    title: str
    description: str
    image_path: Path | None
