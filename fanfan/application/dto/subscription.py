from typing import Optional

from pydantic import BaseModel, ConfigDict

from fanfan.application.dto.event import EventDTO


class CreateSubscriptionDTO(BaseModel):
    user_id: int
    event_id: int
    counter: Optional[int] = None


class SubscriptionDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    event_id: int
    counter: int

    event: EventDTO
