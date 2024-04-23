from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class EventDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: int
    title: str
    position: Optional[int]
    current: Optional[bool]
    skip: bool


class ScheduleEventDTO(EventDTO):
    nomination: Optional[NominationDTO]
    user_subscription: Optional[SubscriptionDTO]


from fanfan.application.dto.nomination import NominationDTO  # noqa: E402
from fanfan.application.dto.subscription import SubscriptionDTO  # noqa: E402

ScheduleEventDTO.model_rebuild()
