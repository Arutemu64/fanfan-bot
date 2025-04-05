from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

from fanfan.core.models.user import UserId

SubscriptionId = NewType("SubscriptionId", int)


@dataclass(slots=True, kw_only=True)
class Subscription:
    id: SubscriptionId | None = None
    user_id: UserId
    event_id: EventId
    counter: int


@dataclass(slots=True, kw_only=True)
class SubscriptionFull(Subscription):
    event: EventFull


from fanfan.core.models.event import EventFull, EventId  # noqa: E402
