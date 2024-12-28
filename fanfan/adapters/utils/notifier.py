import logging

from aiogram import Bot
from aiogram.types import Message

from fanfan.core.dto.notification import UserNotification
from fanfan.core.models.user import UserId

logger = logging.getLogger(__name__)


class BotNotifier:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_notification(
        self, user_id: UserId, notification: UserNotification
    ) -> Message:
        if notification.image_id:
            message = await self.bot.send_photo(
                chat_id=user_id,
                photo=str(notification.image_id),
                caption=notification.render_message_text(),
                reply_markup=notification.reply_markup,
            )
        else:
            message = await self.bot.send_message(
                chat_id=user_id,
                text=notification.render_message_text(),
                reply_markup=notification.reply_markup,
            )
        return message

    async def edit_notification(
        self, message: Message, notification: UserNotification
    ) -> Message:
        if message.caption:
            edited_message = await self.bot.edit_message_caption(
                caption=notification.render_message_text(),
                chat_id=message.chat.id,
                message_id=message.message_id,
                reply_markup=notification.reply_markup,
            )
        else:
            edited_message = await self.bot.edit_message_text(
                text=notification.render_message_text(),
                chat_id=message.chat.id,
                message_id=message.message_id,
                reply_markup=notification.reply_markup,
            )
        return edited_message
