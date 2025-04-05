import enum
from dataclasses import dataclass
from typing import NewType

from fanfan.core.models.event import EventFull, EventId
from fanfan.core.models.mailing import MailingId
from fanfan.core.models.user import User, UserId

ScheduleChangeId = NewType("ScheduleChangeId", int)


class ScheduleChangeType(enum.StrEnum):
    SET_AS_CURRENT = enum.auto()
    # Changed event: current event, None if current was unset
    # Argument event: previously current event

    MOVED = enum.auto()
    # Argument event: previous event by order before moving
    # So if you want to undo this change, you should place
    # changed_event AFTER argument event
    # And if argument_event is None - place changed_event to the top

    SKIPPED = enum.auto()
    # Argument event: None

    UNSKIPPED = enum.auto()
    # Argument event: None


@dataclass(slots=True, kw_only=True)
class ScheduleChange:
    id: ScheduleChangeId | None = None
    type: ScheduleChangeType

    # Arguments
    changed_event_id: EventId
    argument_event_id: EventId | None

    # Mailing
    mailing_id: MailingId | None
    user_id: UserId | None
    send_global_announcement: bool


@dataclass(slots=True, kw_only=True)
class ScheduleChangeFull(ScheduleChange):
    changed_event: EventFull
    argument_event: EventFull | None
    user: User | None
