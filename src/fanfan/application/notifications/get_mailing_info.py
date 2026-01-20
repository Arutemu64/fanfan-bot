from dataclasses import dataclass

from fanfan.adapters.redis.dao.mailing import MailingDAO
from fanfan.core.dto.mailing import MailingDTO
from fanfan.core.vo.mailing import MailingId, MailingStatus


@dataclass(slots=True, frozen=True)
class GetMailingInfoDTO:
    mailing_id: MailingId


@dataclass(slots=True, frozen=True)
class MailingInfoDTO:
    data: MailingDTO
    status: MailingStatus
    sent: int


class GetMailingInfo:
    def __init__(self, mailing_repo: MailingDAO):
        self.mailing_repo = mailing_repo

    async def __call__(self, data: GetMailingInfoDTO) -> MailingInfoDTO:
        mailing_data = await self.mailing_repo.get_mailing_data(data.mailing_id)
        sent_count = await self.mailing_repo.get_sent_count(data.mailing_id)
        mailing_status = MailingStatus.PENDING
        if mailing_data.is_cancelled:
            mailing_status = MailingStatus.CANCELLED
        elif mailing_data.messages_processed >= mailing_data.total_messages:
            mailing_status = MailingStatus.DONE
        elif mailing_data.messages_processed < mailing_data.total_messages:
            mailing_status = MailingStatus.PENDING
        return MailingInfoDTO(data=mailing_data, status=mailing_status, sent=sent_count)
