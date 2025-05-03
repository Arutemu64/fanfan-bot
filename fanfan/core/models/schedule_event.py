from __future__ import annotations

from dataclasses import dataclass
from typing import Any, NewType

from fanfan.core.models.block import ScheduleBlock

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


@dataclass(slots=True, kw_only=True)
class ScheduleEventFull(ScheduleEvent):
    queue: int | None
    nomination: Nomination | None
    block: ScheduleBlock | None


from fanfan.core.models.nomination import Nomination  # noqa: E402
