import typing
from dataclasses import dataclass
from typing import Optional

if typing.TYPE_CHECKING:
    from fanfan.application.dto.nomination import NominationDTO
    from fanfan.application.dto.subscription import SubscriptionDTO


@dataclass(frozen=True, slots=True)
class EventDTO:
    id: int
    title: str
    position: int
    current: Optional[bool]
    skip: bool

    real_position: Optional[int]


@dataclass(frozen=True, slots=True)
class ScheduleEventDTO(EventDTO):
    nomination: Optional["NominationDTO"]
    user_subscription: Optional["SubscriptionDTO"]
