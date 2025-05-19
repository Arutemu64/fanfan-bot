from dataclasses import dataclass

from fanfan.core.vo.schedule_block import ScheduleBlockId


@dataclass(slots=True, kw_only=True)
class ScheduleBlock:
    id: ScheduleBlockId | None = None
    title: str
    start_order: float
