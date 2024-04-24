import logging
from datetime import timedelta
from typing import Annotated, Optional

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from dishka import FromDishka
from dishka.integrations.taskiq import inject
from taskiq import Context, TaskiqDepends

from fanfan.application.dto.notification import UserNotification
from fanfan.infrastructure.di.redis import SchedulerRedis
from fanfan.infrastructure.scheduler import broker

logger = logging.getLogger("__name__")


@broker.task
@inject
async def send_notification(
    notification: UserNotification,
    context: Annotated[Context, TaskiqDepends()],
    bot: FromDishka[Bot],
    redis: FromDishka[SchedulerRedis],
    delivery_id: Optional[str] = None,
) -> dict:
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
        if delivery_id:
            await redis.lpush(f"delivery:{delivery_id}", context.message.task_id)
            await redis.expire(
                f"delivery:{delivery_id}", time=timedelta(hours=1).seconds
            )
        logger.info(
            f"Notification message id={message.message_id} "
            f"was sent to user id={message.chat.id}"
        )
        return message.model_dump(mode="json", exclude_none=True)
    except TelegramBadRequest:
        logger.info(f"Failed to send message to {notification.user_id}, skip")


@broker.task
@inject
async def delete_message(
    message: Message,
    bot: FromDishka[Bot],
) -> None:
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except TelegramBadRequest:
        logger.info(f"Failed to delete message id={message.message_id}, skip")
