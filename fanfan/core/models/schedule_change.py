import enum
from dataclasses import dataclass
from typing import NewType

from fanfan.core.dto.mailing import MailingId
from fanfan.core.models.schedule_event import ScheduleEventId
from fanfan.core.models.user import UserId

ScheduleChangeId = NewType("ScheduleChangeId", int)


class ScheduleChangeType(enum.StrEnum):
    SET_AS_CURRENT = "set_as_current"
    # Changed event: current event
    # Argument event: previously current event

    MOVED = "moved"
    # Argument event: previous event by order before moving
    # So if you want to undo this change, you should place
    # changed_event AFTER argument event
    # And if argument_event is None - place changed_event to the top

    SKIPPED = "skipped"
    # Argument event: None

    UNSKIPPED = "unskipped"
    # Argument event: None


@dataclass(slots=True, kw_only=True)
class ScheduleChange:
    id: ScheduleChangeId | None = None
    type: ScheduleChangeType

    # Arguments
    changed_event_id: ScheduleEventId
    argument_event_id: ScheduleEventId | None

    # Mailing
    mailing_id: MailingId | None
    user_id: UserId | None
    send_global_announcement: bool
