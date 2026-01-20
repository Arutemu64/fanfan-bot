from dataclasses import dataclass

from fanfan.core.events.base import AppEvent
from fanfan.core.vo.schedule_change import ScheduleChangeId


@dataclass(kw_only=True, slots=True)
class NewScheduleChange(AppEvent):
    subject: str = "schedule.change.new"

    schedule_change_id: ScheduleChangeId
