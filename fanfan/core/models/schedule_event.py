from __future__ import annotations

from dataclasses import dataclass
from typing import Any, NewType

from fanfan.core.models.participant import ParticipantId

ScheduleEventId = NewType("ScheduleEventId", int)
ScheduleEventPublicId = NewType("ScheduleEventPublicId", int)


@dataclass(slots=True, kw_only=True)
class ScheduleEvent:
    id: ScheduleEventId | None = None
    public_id: ScheduleEventPublicId
    title: str
    duration: int
    order: float
    is_current: bool | None
    is_skipped: bool
    participant_id: ParticipantId | None

    def __eq__(self, other: ScheduleEvent | Any) -> bool:
        return isinstance(other, ScheduleEvent) and self.id == other.id
