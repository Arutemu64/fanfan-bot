from dataclasses import dataclass

from fanfan.core.models.schedule_event import ScheduleEventId
from fanfan.core.models.subscription import SubscriptionId
from fanfan.core.models.user import UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class SubscriptionEventDTO:
    id: ScheduleEventId
    title: str
    is_skipped: bool
    order: int
    queue: int | None
    time_until: int


@dataclass(frozen=True, slots=True, kw_only=True)
class SubscriptionDTO:
    id: SubscriptionId
    user_id: UserId
    counter: int
    event: SubscriptionEventDTO
