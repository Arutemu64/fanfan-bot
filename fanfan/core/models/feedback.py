from dataclasses import dataclass
from typing import NewType

from fanfan.core.models.user import UserId

FeedbackId = NewType("FeedbackId", int)


@dataclass(frozen=True, slots=True)
class FeedbackModel:
    user_id: UserId
    text: str
    asap: bool
    id: FeedbackId | None = None
