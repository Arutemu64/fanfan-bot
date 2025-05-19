from dataclasses import dataclass

from fanfan.core.dto.mailing import MailingId
from fanfan.core.vo.feedback import FeedbackId
from fanfan.core.vo.user import UserId


@dataclass(slots=True, kw_only=True)
class Feedback:
    id: FeedbackId | None = None
    text: str
    user_id: UserId | None
    processed_by_id: UserId | None
    mailing_id: MailingId

    def set_mailing_id(self, mailing_id: MailingId) -> None:
        self.mailing_id = mailing_id
