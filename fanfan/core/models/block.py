from dataclasses import dataclass
from typing import NewType

ScheduleBlockId = NewType("ScheduleBlockId", int)


@dataclass(slots=True, kw_only=True)
class ScheduleBlock:
    id: ScheduleBlockId
    title: str
