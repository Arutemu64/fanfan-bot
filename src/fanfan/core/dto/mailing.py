from dataclasses import dataclass

from fanfan.core.vo.mailing import MailingId
from fanfan.core.vo.user import UserId


@dataclass(slots=True, kw_only=True, frozen=True)
class MailingDTO:
    id: MailingId
    total_messages: int
    messages_processed: int
    is_cancelled: bool
    by_user_id: UserId
