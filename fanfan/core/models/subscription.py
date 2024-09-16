from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SubscriptionDTO:
    id: int
    user_id: int
    event_id: int
    counter: int


@dataclass(frozen=True, slots=True)
class FullSubscriptionDTO(SubscriptionDTO):
    event: EventDTO


from fanfan.core.models.event import EventDTO  # noqa: E402
