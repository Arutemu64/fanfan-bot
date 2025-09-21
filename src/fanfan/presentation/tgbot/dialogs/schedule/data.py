from dataclasses import dataclass

from fanfan.core.vo.schedule_event import ScheduleEventId


@dataclass(slots=True)
class ScheduleDialogData:
    event_id: ScheduleEventId | None = None
