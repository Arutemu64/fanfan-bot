from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

from fanfan.core.models.block import BlockModel

EventId = NewType("EventId", int)


@dataclass(frozen=True, slots=True)
class EventModel:
    id: EventId
    title: str
    current: bool | None
    skip: bool
    order: float
    queue: int | None


@dataclass(frozen=True, slots=True)
class FullEventModel(EventModel):
    nomination: NominationModel | None
    block: BlockModel | None
    user_subscription: SubscriptionModel | None


from fanfan.core.models.nomination import NominationModel  # noqa: E402
from fanfan.core.models.subscription import SubscriptionModel  # noqa: E402
