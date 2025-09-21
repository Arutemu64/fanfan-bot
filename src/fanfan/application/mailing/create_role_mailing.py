import logging
from dataclasses import dataclass

from fanfan.adapters.redis.dao.mailing import MailingDAO
from fanfan.adapters.utils.events_broker import EventsBroker
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.notification import UserNotification
from fanfan.core.events.notifications import NewRolesNotificationEvent
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.vo.mailing import MailingId
from fanfan.core.vo.user import UserRole

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CreateRoleMailingDTO:
    text: str
    roles: list[UserRole]
    image_id: str | None = None


class CreateRoleMailing:
    def __init__(
        self,
        id_provider: IdProvider,
        mailing_repo: MailingDAO,
        stream_broker_adapter: EventsBroker,
    ):
        self.id_provider = id_provider
        self.mailing_repo = mailing_repo
        self.stream_broker_adapter = stream_broker_adapter

    async def __call__(self, data: CreateRoleMailingDTO) -> MailingId:
        sender = await self.id_provider.get_current_user()
        if sender.role is not UserRole.ORG:
            raise AccessDenied

        mailing_id = await self.mailing_repo.create_new_mailing(by_user_id=sender.id)
        await self.stream_broker_adapter.publish(
            NewRolesNotificationEvent(
                notification=UserNotification(
                    title="📣 Сообщение от организаторов",
                    text=f"<blockquote>{data.text}</blockquote>",
                    bottom_text=f"Отправил @{sender.username}",
                    image_id=data.image_id,
                ),
                roles=data.roles,
                mailing_id=mailing_id,
            )
        )
        logger.info(
            "New roles mailing initiated by user %s",
            sender.id,
            extra={"mailing_id": mailing_id},
        )
        return mailing_id
