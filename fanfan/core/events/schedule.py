from dataclasses import dataclass

from fanfan.core.events.base import AppEvent
from fanfan.core.models.schedule_change import ScheduleChangeId


@dataclass(kw_only=True, slots=True)
class ScheduleChangedEvent(AppEvent):
    subject: str = "schedule.changed"

    schedule_change_id: ScheduleChangeId
