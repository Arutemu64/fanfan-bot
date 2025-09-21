from dataclasses import dataclass

from fanfan.core.events.base import AppEvent
from fanfan.core.models.schedule_change import ScheduleChangeType
from fanfan.core.vo.mailing import MailingId
from fanfan.core.vo.schedule_event import ScheduleEventId
from fanfan.core.vo.user import UserId


@dataclass(kw_only=True, slots=True)
class ScheduleChanged(AppEvent):
    subject: str = "schedule.change.new"

    type: ScheduleChangeType
    changed_event_id: ScheduleEventId
    argument_event_id: ScheduleEventId | None

    mailing_id: MailingId
    user_id: UserId
    send_global_announcement: bool
