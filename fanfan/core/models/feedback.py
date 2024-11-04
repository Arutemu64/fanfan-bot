from dataclasses import dataclass
from typing import NewType

from fanfan.core.dto.mailing import MailingId
from fanfan.core.models.user import UserId, UserModel

FeedbackId = NewType("FeedbackId", int)


@dataclass(slots=True)
class FeedbackModel:
    text: str
    user_id: UserId | None
    processed_by_id: UserId | None
    mailing_id: MailingId | None
    id: FeedbackId | None = None


@dataclass(slots=True, kw_only=True)
class FullFeedbackModel(FeedbackModel):
    user: UserModel
    processed_by: UserModel
