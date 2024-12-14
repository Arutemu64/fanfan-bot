import logging

from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.adapters.utils.stream_broker import StreamBrokerAdapter
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.models.mailing import Mailing, MailingId
from fanfan.core.models.user import UserRole

logger = logging.getLogger(__name__)


class CancelMailing(Interactor[MailingId, Mailing]):
    def __init__(
        self,
        mailing_repo: MailingRepository,
        id_provider: IdProvider,
        stream_broker_adapter: StreamBrokerAdapter,
    ):
        self.mailing_repo = mailing_repo
        self.id_provider = id_provider
        self.stream_broker_adapter = stream_broker_adapter

    async def __call__(self, mailing_id: MailingId) -> Mailing:
        mailing_info = await self.mailing_repo.get_mailing_data(mailing_id)
        user = await self.id_provider.get_current_user()
        if (mailing_info.by_user_id == user.id) or (user.role is UserRole.ORG):
            await self.stream_broker_adapter.cancel_mailing(mailing_id)
            logger.info(
                "Mailing %s deleted by user %s",
                mailing_id,
                user.id,
                extra={"mailing_info": mailing_info},
            )
            return mailing_info
        raise AccessDenied
