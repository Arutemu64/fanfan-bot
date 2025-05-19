import logging

from fanfan.adapters.redis.dao.mailing import MailingDAO
from fanfan.adapters.utils.events_broker import EventsBroker
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.mailing import MailingDTO, MailingId
from fanfan.core.events.notifications import CancelMailingEvent
from fanfan.core.services.access import UserAccessValidator

logger = logging.getLogger(__name__)


class CancelMailing:
    def __init__(
        self,
        mailing_repo: MailingDAO,
        id_provider: IdProvider,
        stream_broker_adapter: EventsBroker,
        access: UserAccessValidator,
    ):
        self.mailing_repo = mailing_repo
        self.id_provider = id_provider
        self.stream_broker_adapter = stream_broker_adapter
        self.access = access

    async def __call__(self, mailing_id: MailingId) -> MailingDTO:
        mailing = await self.mailing_repo.get_mailing_data(mailing_id)
        user = await self.id_provider.get_user_data()
        self.access.ensure_can_cancel_mailing(mailing=mailing, user=user)
        await self.stream_broker_adapter.publish(
            CancelMailingEvent(mailing_id=mailing_id)
        )
        logger.info(
            "Mailing %s deleted by user %s",
            mailing_id,
            user.id,
            extra={"mailing": mailing},
        )
        return mailing
