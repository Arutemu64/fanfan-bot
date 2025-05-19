from dataclasses import dataclass

from fanfan.adapters.redis.dao.mailing import MailingDAO
from fanfan.core.dto.mailing import MailingDTO, MailingId, MailingStatus


@dataclass(slots=True, frozen=True)
class MailingInfoDTO:
    data: MailingDTO
    status: MailingStatus
    sent: int


class ReadMailingInfo:
    def __init__(self, mailing_repo: MailingDAO):
        self.mailing_repo = mailing_repo

    async def __call__(self, mailing_id: MailingId) -> MailingInfoDTO:
        data = await self.mailing_repo.get_mailing_data(mailing_id)
        sent = await self.mailing_repo.get_sent_count(mailing_id)
        status = MailingStatus.PENDING
        if data.is_cancelled:
            status = MailingStatus.CANCELLED
        elif data.messages_processed >= data.total_messages:
            status = MailingStatus.DONE
        elif data.messages_processed < data.total_messages:
            status = MailingStatus.PENDING
        return MailingInfoDTO(data=data, status=status, sent=sent)
