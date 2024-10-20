import logging

from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.application.common.notifier import Notifier
from fanfan.core.enums import UserRole
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.models.mailing import MailingData, MailingId

logger = logging.getLogger(__name__)


class DeleteMailing(Interactor[MailingId, MailingData]):
    def __init__(
        self,
        mailing_repo: MailingRepository,
        id_provider: IdProvider,
        notifier: Notifier,
    ):
        self.mailing_repo = mailing_repo
        self.id_provider = id_provider
        self.notifier = notifier

    async def __call__(self, mailing_id: MailingId) -> MailingData:
        mailing_info = await self.mailing_repo.get_mailing_info(mailing_id)
        user = await self.id_provider.get_current_user()
        if (mailing_info.by_user_id == user.id) or (user.role is UserRole.ORG):
            await self.notifier.delete_mailing(mailing_id)
            logger.info(
                "Mailing %s deleted by user %s",
                mailing_id,
                user.id,
                extra={"mailing_info": mailing_info},
            )
            return mailing_info
        raise AccessDenied
