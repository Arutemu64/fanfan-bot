from dataclasses import dataclass

from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.application.common.interactor import Interactor
from fanfan.core.models.mailing import MailingData, MailingId


@dataclass(slots=True, frozen=True)
class MailingInfoDTO:
    data: MailingData
    sent: int


class GetMailingInfo(Interactor[MailingId, MailingInfoDTO]):
    def __init__(self, mailing_repo: MailingRepository):
        self.mailing_repo = mailing_repo

    async def __call__(self, mailing_id: MailingId) -> MailingInfoDTO:
        return MailingInfoDTO(
            data=await self.mailing_repo.get_mailing_info(mailing_id),
            sent=await self.mailing_repo.get_sent_count(mailing_id),
        )
