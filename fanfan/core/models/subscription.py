from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

from fanfan.core.models.user import UserId

SubscriptionId = NewType("SubscriptionId", int)


@dataclass(slots=True)
class SubscriptionModel:
    user_id: UserId
    event_id: EventId
    counter: int
    id: SubscriptionId | None = None


@dataclass(slots=True, kw_only=True)
class FullSubscriptionModel(SubscriptionModel):
    event: FullEventModel


from fanfan.core.models.event import EventId, FullEventModel  # noqa: E402
