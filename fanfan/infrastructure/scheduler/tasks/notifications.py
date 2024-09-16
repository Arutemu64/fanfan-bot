import logging
from datetime import timedelta

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import Message
from dishka import FromDishka
from dishka.integrations.taskiq import inject
from redis.asyncio import Redis

from fanfan.core.models.notification import UserNotification
from fanfan.infrastructure.scheduler import broker

logger = logging.getLogger("__name__")


@broker.task()
@inject
async def send_notification(
    notification: UserNotification,
    bot: FromDishka[Bot],
    redis: FromDishka[Redis],
    mailing_id: str | None = None,
) -> None:
    try:
        if notification.image_id:
            message = await bot.send_photo(
                chat_id=notification.user_id,
                photo=str(notification.image_id),
                caption=notification.render_message_text(),
                reply_markup=notification.reply_markup,
            )
        else:
            message = await bot.send_message(
                chat_id=notification.user_id,
                text=notification.render_message_text(),
                reply_markup=notification.reply_markup,
            )
        if mailing_id:
            await redis.lpush(
                f"mailing:{mailing_id}",
                message.model_dump_json(exclude_none=True),
            )
            await redis.expire(
                f"mailing:{mailing_id}",
                time=timedelta(hours=1).seconds,
            )
    except (TelegramBadRequest, TelegramForbiddenError):
        logger.info("Failed to send message to user %s, skip", notification.user_id)


@broker.task()
@inject
async def delete_message(
    message: Message,
    bot: FromDishka[Bot],
) -> None:
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except (TelegramBadRequest, TelegramForbiddenError):
        logger.info("Failed to delete message id %s, skip", message.message_id)
