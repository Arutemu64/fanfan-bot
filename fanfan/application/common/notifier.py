import logging

from aiogram import Bot
from faststream.nats import NatsBroker

from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.enums import UserRole
from fanfan.core.models.mailing import MailingData, MailingId
from fanfan.core.models.notification import SendNotificationDTO, UserNotification
from fanfan.presentation.stream.routes.prepare_announcements import (
    EventChangeDTO,
    PrepareAnnouncementsDTO,
)
from fanfan.presentation.stream.routes.send_to_roles import (
    SendNotificationToRolesDTO,
)

logger = logging.getLogger(__name__)


class Notifier:
    def __init__(
        self,
        mailing_repo: MailingRepository,
        broker: NatsBroker,
        bot: Bot,
        id_provider: IdProvider,
        users_repo: UsersRepository,
    ):
        self.mailing_repo = mailing_repo
        self.broker = broker
        self.bot = bot
        self.id_provider = id_provider
        self.users_repo = users_repo

    async def show_notification(self, notification: UserNotification):
        user_id = self.id_provider.get_current_user_id()
        if notification.image_id:
            await self.bot.send_photo(
                chat_id=user_id,
                photo=str(notification.image_id),
                caption=notification.render_message_text(),
                reply_markup=notification.reply_markup,
            )
        else:
            await self.bot.send_message(
                chat_id=user_id,
                text=notification.render_message_text(),
                reply_markup=notification.reply_markup,
            )

    async def send_notification(self, dto: SendNotificationDTO) -> None:
        await self.broker.publish(dto, subject="send_notification")

    async def send_to_roles(
        self, notification: UserNotification, roles: list[UserRole]
    ) -> MailingData:
        mailing_data = await self.mailing_repo.create_new_mailing(
            by_user_id=self.id_provider.get_current_user_id()
        )
        await self.broker.publish(
            SendNotificationToRolesDTO(
                notification=notification, roles=roles, mailing_id=mailing_data.id
            ),
            subject="send_to_roles",
        )
        return mailing_data

    async def send_announcements(
        self,
        send_global_announcement: bool,
        event_changes: list[EventChangeDTO],
    ) -> MailingData:
        mailing_data = await self.mailing_repo.create_new_mailing(
            by_user_id=self.id_provider.get_current_user_id()
        )
        await self.broker.publish(
            PrepareAnnouncementsDTO(
                send_global_announcement=send_global_announcement,
                event_changes=event_changes,
                mailing_id=mailing_data.id,
            ),
            subject="prepare_announcements",
        )
        return mailing_data

    async def delete_mailing(self, mailing_id: MailingId) -> None:
        await self.broker.publish(mailing_id, subject="delete_mailing")
