from __future__ import annotations

import datetime
from typing import Optional, Self

from pydantic import BaseModel, ConfigDict


class CreateEventDTO(BaseModel):
    id: int
    title: str

    order: Optional[float] = None
    participant_id: Optional[int] = None


class EventDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: int
    title: str
    order: float
    current: Optional[bool]
    skip: bool
    updated_on: datetime.datetime

    def __eq__(self, other: Optional[Self]) -> bool:
        if other is None:
            return False
        return self.id == other.id


class SubscriptionEventDTO(EventDTO):
    position: int


class ScheduleEventDTO(EventDTO):
    nomination: Optional[NominationDTO]
    user_subscription: Optional[SubscriptionDTO]


class FullEventDTO(EventDTO):
    position: Optional[int]
    nomination: Optional[NominationDTO]
    user_subscription: Optional[SubscriptionDTO]


class UpdateEventDTO(BaseModel):
    id: int
    title: Optional[str] = None
    order: Optional[float] = None
    current: Optional[bool] = None
    skip: Optional[bool] = None
    participant_id: Optional[int] = None


from fanfan.application.dto.nomination import NominationDTO  # noqa: E402
from fanfan.application.dto.subscription import SubscriptionDTO  # noqa: E402

ScheduleEventDTO.model_rebuild()
