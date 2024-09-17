from __future__ import annotations

from dataclasses import dataclass

from fanfan.core.models.block import BlockDTO


@dataclass(frozen=True, slots=True)
class EventDTO:
    id: int
    title: str
    current: bool | None
    skip: bool

    queue: int | None


@dataclass(frozen=True, slots=True)
class FullEventDTO(EventDTO):
    nomination: NominationDTO | None
    block: BlockDTO | None


@dataclass(frozen=True, slots=True)
class UserFullEventDTO(FullEventDTO):
    subscription: SubscriptionDTO | None


from fanfan.core.models.nomination import NominationDTO  # noqa: E402
from fanfan.core.models.subscription import SubscriptionDTO  # noqa: E402
