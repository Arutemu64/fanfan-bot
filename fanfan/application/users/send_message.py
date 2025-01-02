import logging
from dataclasses import dataclass

from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.adapters.utils.stream_broker import StreamBrokerAdapter
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.dto.notification import UserNotification
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import UserId, UserRole
from fanfan.presentation.stream.routes.notifications.send_notification import (
    SendNotificationDTO,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class SendMessageDTO:
    user_id: UserId
    message_text: str


class SendMessage(Interactor[SendMessageDTO, None]):
    def __init__(
        self,
        users_repo: UsersRepository,
        mailing_repo: MailingRepository,
        id_provider: IdProvider,
        stream_broker_adapter: StreamBrokerAdapter,
    ):
        self.users_repo = users_repo
        self.mailing_repo = mailing_repo
        self.id_provider = id_provider
        self.stream_broker_adapter = stream_broker_adapter

    async def __call__(self, data: SendMessageDTO):
        current_user = await self.id_provider.get_current_user()
        if current_user.role != UserRole.ORG:
            raise AccessDenied

        user = await self.users_repo.get_user_by_id(data.user_id)
        if user is None:
            raise UserNotFound

        mailing_id = await self.mailing_repo.create_new_mailing(
            by_user_id=current_user.id
        )
        await self.stream_broker_adapter.send_notification(
            data=SendNotificationDTO(
                user_id=user.id,
                notification=UserNotification(
                    title="🗨️ Личное сообщение от оргов",
                    text=f"<blockquote>{data.message_text}</blockquote>",
                    bottom_text=f"<i>Отправил @{current_user.username}</i>",
                ),
            ),
            mailing_id=mailing_id,
        )

        logger.info(
            "Org %s sent message to user %s with mailing id %s",
            current_user.id,
            user.id,
            mailing_id,
            extra={"data": data},
        )
