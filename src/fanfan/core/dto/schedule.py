from dataclasses import dataclass

from fanfan.core.vo.nomination import NominationId
from fanfan.core.vo.schedule_block import ScheduleBlockId
from fanfan.core.vo.schedule_event import ScheduleEventId, ScheduleEventPublicId
from fanfan.core.vo.subscription import SubscriptionId


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
    public_id: ScheduleEventPublicId
    title: str
    is_current: bool | None
    is_skipped: bool
    order: float
    duration: int
    queue: int | None
    cumulative_duration: int | None
    nomination: ScheduleEventNominationDTO | None
    block: ScheduleEventBlockDTO | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ScheduleEventUserDTO(ScheduleEventDTO):
    subscription: ScheduleEventSubscriptionDTO | None
