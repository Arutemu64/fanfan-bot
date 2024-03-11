from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

from fanfan.application.dto.event import EventDTO


class CreateSubscriptionDTO(BaseModel):
    user_id: int
    event_id: int
    counter: Optional[int] = None


@dataclass(frozen=True, slots=True)
class SubscriptionDTO:
    id: int
    user_id: int
    event_id: int
    counter: int

    event: EventDTO
