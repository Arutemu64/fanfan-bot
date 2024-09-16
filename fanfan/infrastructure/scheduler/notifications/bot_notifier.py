import logging
import uuid

from aiogram import Bot
from aiogram.types import Message
from redis.asyncio import Redis

from fanfan.core.models.notification import MailingInfo, UserNotification
from fanfan.infrastructure.scheduler.tasks import delete_message, send_notification

logger = logging.getLogger(__name__)


class Notifier:
    def __init__(self, bot: Bot, redis: Redis) -> None:
        self.bot = bot
        self.redis = redis

    async def send_notification(self, notification: UserNotification) -> Message:
        if notification.image_id:
            message = await self.bot.send_photo(
                chat_id=notification.user_id,
                photo=str(notification.image_id),
                caption=notification.render_message_text(),
                reply_markup=notification.reply_markup,
            )
        else:
            message = await self.bot.send_message(
                chat_id=notification.user_id,
                text=notification.render_message_text(),
                reply_markup=notification.reply_markup,
            )
        return message

    async def schedule_mailing(
        self,
        notifications: list[UserNotification],
        mailing_id: str | None = None,
    ) -> MailingInfo:
        if mailing_id is None:
            mailing_id = uuid.uuid4().hex
        logger.info("Mailing started", extra={"mailing_id": mailing_id})
        for notification in notifications:
            await send_notification.kiq(
                notification=notification,
                mailing_id=mailing_id,
            )
        return MailingInfo(mailing_id=mailing_id, count=len(notifications))

    async def delete_mailing(self, mailing_id: str) -> MailingInfo:
        key = f"mailing:{mailing_id}"
        count = 0
        while await self.redis.llen(key) > 0:
            await delete_message.kiq(
                message=Message.model_validate_json(await self.redis.lpop(key)),
            )
            count += 1
        mailing_info = MailingInfo(mailing_id=mailing_id, count=count)
        logger.info("Mailing was deleted", extra={"mailing_info": mailing_info})
        return mailing_info
