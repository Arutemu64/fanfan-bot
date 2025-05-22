from dataclasses import dataclass

from fanfan.core.vo.schedule_event import ScheduleEventId, ScheduleEventPublicId
from fanfan.core.vo.subscription import SubscriptionId
from fanfan.core.vo.user import UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class SubscriptionEventDTO:
    id: ScheduleEventId
    public_id: ScheduleEventPublicId
    title: str
    is_skipped: bool
    order: int
    queue: int | None
    cumulative_duration: int | None


@dataclass(frozen=True, slots=True, kw_only=True)
class SubscriptionDTO:
    id: SubscriptionId
    user_id: UserId
    counter: int
    event: SubscriptionEventDTO
