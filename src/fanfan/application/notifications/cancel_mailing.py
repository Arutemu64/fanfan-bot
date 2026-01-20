import logging
from dataclasses import dataclass

from fanfan.adapters.nats.events_broker import EventsBroker
from fanfan.adapters.redis.dao.mailing import MailingDAO
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.mailing import MailingDTO
from fanfan.core.events.notifications import CancelMailingEvent
from fanfan.core.services.mailing import MailingService
from fanfan.core.vo.mailing import MailingId

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class CancelMailingDTO:
    mailing_id: MailingId


class CancelMailing:
    def __init__(
        self,
        mailing_repo: MailingDAO,
        id_provider: IdProvider,
        stream_broker_adapter: EventsBroker,
        service: MailingService,
    ):
        self.mailing_repo = mailing_repo
        self.id_provider = id_provider
        self.stream_broker_adapter = stream_broker_adapter
        self.service = service

    async def __call__(self, data: CancelMailingDTO) -> MailingDTO:
        mailing = await self.mailing_repo.get_mailing_data(data.mailing_id)
        user = await self.id_provider.get_current_user()
        self.service.ensure_user_can_cancel_mailing(mailing=mailing, user=user)
        await self.stream_broker_adapter.publish(
            CancelMailingEvent(mailing_id=data.mailing_id)
        )
        logger.info(
            "Mailing %s deleted by user %s",
            data.mailing_id,
            user.id,
            extra={"mailing": mailing},
        )
        return mailing
