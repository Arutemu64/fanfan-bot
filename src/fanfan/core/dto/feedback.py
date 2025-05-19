from dataclasses import dataclass

from fanfan.core.dto.mailing import MailingId
from fanfan.core.vo.feedback import FeedbackId
from fanfan.core.vo.user import UserId


@dataclass(slots=True, kw_only=True, frozen=True)
class FeedbackUserDTO:
    id: UserId
    username: str


@dataclass(frozen=True, kw_only=True, slots=True)
class FeedbackDTO:
    id: FeedbackId
    text: str
    mailing_id: MailingId

    reported_by: FeedbackUserDTO
    processed_by: FeedbackUserDTO
