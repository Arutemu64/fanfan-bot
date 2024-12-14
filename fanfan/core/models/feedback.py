from dataclasses import dataclass
from typing import NewType

from fanfan.core.models.mailing import MailingId
from fanfan.core.models.user import User, UserId

FeedbackId = NewType("FeedbackId", int)


@dataclass(slots=True, kw_only=True)
class Feedback:
    id: FeedbackId | None = None
    text: str
    user_id: UserId | None
    processed_by_id: UserId | None
    mailing_id: MailingId | None


@dataclass(slots=True, kw_only=True)
class FullFeedback(Feedback):
    user: User
    processed_by: User
