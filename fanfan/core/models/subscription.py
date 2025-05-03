from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

from fanfan.core.models.user import UserId

SubscriptionId = NewType("SubscriptionId", int)


@dataclass(slots=True, kw_only=True)
class Subscription:
    id: SubscriptionId | None = None
    user_id: UserId
    event_id: ScheduleEventId
    counter: int


@dataclass(slots=True, kw_only=True)
class SubscriptionFull(Subscription):
    event: ScheduleEventFull


from fanfan.core.models.schedule_event import (  # noqa: E402
    ScheduleEventFull,
    ScheduleEventId,
)
