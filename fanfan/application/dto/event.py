from typing import Optional

from pydantic import BaseModel, ConfigDict


class EventDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    position: int
    real_position: Optional[int]

    current: Optional[bool]
    skip: bool


class FullEventDTO(EventDTO):
    nomination: Optional["NominationDTO"]
    user_subscription: Optional["SubscriptionDTO"]


from fanfan.application.dto.nomination import NominationDTO  # noqa: E402
from fanfan.application.dto.subscription import SubscriptionDTO  # noqa: E402

FullEventDTO.model_rebuild()
