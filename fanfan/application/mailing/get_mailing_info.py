from fanfan.application.common.interactor import Interactor
from fanfan.core.models.mailing import MailingData, MailingId
from fanfan.infrastructure.redis.repositories.mailing import MailingRepository


class GetMailingInfo(Interactor[MailingId, MailingData]):
    def __init__(self, mailing_repo: MailingRepository):
        self.mailing_repo = mailing_repo

    async def __call__(self, mailing_id: MailingId) -> MailingData:
        return await self.mailing_repo.get_mailing_info(mailing_id)
