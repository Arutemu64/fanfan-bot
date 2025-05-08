from dataclasses import dataclass
from typing import NewType

from fanfan.core.dto.mailing import MailingId
from fanfan.core.models.user import UserId

FeedbackId = NewType("FeedbackId", int)


@dataclass(slots=True, kw_only=True)
class Feedback:
    id: FeedbackId | None = None
    text: str
    user_id: UserId | None
    processed_by_id: UserId | None
    mailing_id: MailingId

    def set_mailing_id(self, mailing_id: MailingId) -> None:
        self.mailing_id = mailing_id
