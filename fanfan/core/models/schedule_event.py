from __future__ import annotations

from dataclasses import dataclass
from typing import Any, NewType

ScheduleEventId = NewType("ScheduleEventId", int)


@dataclass(slots=True, kw_only=True)
class ScheduleEvent:
    id: ScheduleEventId
    title: str
    order: float
    is_current: bool | None
    is_skipped: bool

    def __eq__(self, other: ScheduleEvent | Any) -> bool:
        return bool(isinstance(other, ScheduleEvent) and self.id == other.id)
