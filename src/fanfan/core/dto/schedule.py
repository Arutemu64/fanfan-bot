from dataclasses import dataclass

from fanfan.core.vo.schedule_event import ScheduleEventId, ScheduleEventPublicId
from fanfan.core.vo.subscription import SubscriptionId


@dataclass(frozen=True, slots=True, kw_only=True)
class ScheduleEventSubscriptionDTO:
    id: SubscriptionId
    counter: int


@dataclass(frozen=True, slots=True, kw_only=True)
class ScheduleEventDTO:
    id: ScheduleEventId
    public_id: ScheduleEventPublicId
    title: str
    duration: int
    order: float
    is_current: bool | None
    is_skipped: bool
    nomination_title: str
    block_title: str

    # Calculated values
    queue: int | None
    cumulative_duration: int | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ScheduleEventUserDTO(ScheduleEventDTO):
    subscription: ScheduleEventSubscriptionDTO | None
