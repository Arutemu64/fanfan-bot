from dataclasses import dataclass

from fanfan.core.models.block import ScheduleBlockId
from fanfan.core.models.nomination import NominationId
from fanfan.core.models.schedule_event import ScheduleEventId
from fanfan.core.models.subscription import SubscriptionId


@dataclass(frozen=True, slots=True, kw_only=True)
class ScheduleEventNominationDTO:
    id: NominationId
    title: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ScheduleEventBlockDTO:
    id: ScheduleBlockId
    title: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ScheduleEventSubscriptionDTO:
    id: SubscriptionId
    counter: int


@dataclass(frozen=True, slots=True, kw_only=True)
class ScheduleEventDTO:
    id: ScheduleEventId
    title: str
    is_current: bool | None
    is_skipped: bool
    order: float
    duration: int
    queue: int | None
    time_until: int
    nomination: ScheduleEventNominationDTO | None
    block: ScheduleEventBlockDTO | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ScheduleEventUserDTO(ScheduleEventDTO):
    subscription: ScheduleEventSubscriptionDTO | None
