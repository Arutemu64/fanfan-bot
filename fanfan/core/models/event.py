from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

from fanfan.core.models.block import Block

EventId = NewType("EventId", int)


@dataclass(slots=True, kw_only=True)
class Event:
    id: EventId
    title: str
    order: float
    is_current: bool | None
    is_skipped: bool


@dataclass(slots=True, kw_only=True)
class FullEvent(Event):
    queue: int | None
    nomination: Nomination | None
    block: Block | None
    user_subscription: Subscription | None


from fanfan.core.models.nomination import Nomination  # noqa: E402
from fanfan.core.models.subscription import Subscription  # noqa: E402
