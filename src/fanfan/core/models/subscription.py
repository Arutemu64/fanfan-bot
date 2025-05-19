from __future__ import annotations

from dataclasses import dataclass

from fanfan.core.vo.schedule_event import ScheduleEventId
from fanfan.core.vo.subscription import SubscriptionId
from fanfan.core.vo.user import UserId


@dataclass(slots=True, kw_only=True)
class Subscription:
    id: SubscriptionId | None = None
    user_id: UserId
    event_id: ScheduleEventId
    counter: int
