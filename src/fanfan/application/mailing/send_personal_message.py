import logging
from dataclasses import dataclass

from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.redis.dao.mailing import MailingDAO
from fanfan.adapters.utils.events_broker import EventsBroker
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.notification import UserNotification
from fanfan.core.events.notifications import NewNotificationEvent
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.vo.user import UserId, UserRole

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class SendPersonalMessageDTO:
    user_id: UserId
    message_text: str


class SendPersonalMessage:
    def __init__(
        self,
        users_repo: UsersRepository,
        mailing_dao: MailingDAO,
        id_provider: IdProvider,
        stream_broker_adapter: EventsBroker,
    ):
        self.users_repo = users_repo
        self.mailing_dao = mailing_dao
        self.id_provider = id_provider
        self.stream_broker_adapter = stream_broker_adapter

    async def __call__(self, data: SendPersonalMessageDTO):
        current_user = await self.id_provider.get_user_data()
        if current_user.role != UserRole.ORG:
            raise AccessDenied

        user = await self.users_repo.read_user_by_id(data.user_id)
        if user is None:
            raise UserNotFound

        mailing_id = await self.mailing_dao.create_new_mailing(
            by_user_id=current_user.id
        )
        await self.stream_broker_adapter.publish(
            NewNotificationEvent(
                user_id=user.id,
                notification=UserNotification(
                    title="💌 Личное сообщение",
                    text=f"<blockquote>{data.message_text}</blockquote>",
                    bottom_text=f"<i>Отправил @{current_user.username}</i>",
                ),
                mailing_id=mailing_id,
            )
        )

        logger.info(
            "Org %s sent message to user %s with mailing id %s",
            current_user.id,
            user.id,
            mailing_id,
            extra={"data": data},
        )
