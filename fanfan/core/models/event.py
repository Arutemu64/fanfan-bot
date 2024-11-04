from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

from fanfan.core.models.block import BlockModel

EventId = NewType("EventId", int)


@dataclass(slots=True)
class EventModel:
    id: EventId
    title: str
    current: bool | None
    skip: bool
    order: float


@dataclass(slots=True)
class FullEventModel(EventModel):
    queue: int | None
    nomination: NominationModel | None
    block: BlockModel | None
    user_subscription: SubscriptionModel | None


from fanfan.core.models.nomination import NominationModel  # noqa: E402
from fanfan.core.models.subscription import SubscriptionModel  # noqa: E402
