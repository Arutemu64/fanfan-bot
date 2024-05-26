import logging
from datetime import timedelta
from typing import List, Optional

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import Message
from aiogram_dialog import BgManagerFactory, ShowMode
from dishka import FromDishka
from dishka.integrations.taskiq import inject
from redis.asyncio import Redis

from fanfan.application.dto.notification import UserNotification
from fanfan.infrastructure.scheduler import broker

logger = logging.getLogger("__name__")


@broker.task()
@inject
async def send_notification(
    user_id: int,
    user_notifications: List[UserNotification],
    bot: FromDishka[Bot],
    redis: FromDishka[Redis],
    dialog_bg_factory: FromDishka[BgManagerFactory],
    delivery_id: Optional[str] = None,
) -> None:
    try:
        for notification in user_notifications:
            if notification.image_id:
                message = await bot.send_photo(
                    chat_id=user_id,
                    photo=str(notification.image_id),
                    caption=notification.render_message_text(),
                    reply_markup=notification.reply_markup,
                )
            else:
                message = await bot.send_message(
                    chat_id=user_id,
                    text=notification.render_message_text(),
                    reply_markup=notification.reply_markup,
                )
            if delivery_id:
                await redis.lpush(
                    f"delivery:{delivery_id}",
                    message.model_dump_json(exclude_none=True),
                )
                await redis.expire(
                    f"delivery:{delivery_id}", time=timedelta(hours=1).seconds
                )
        bg = dialog_bg_factory.bg(
            bot=bot,
            user_id=user_id,
            chat_id=user_id,
            load=True,
        )
        await bg.update(data={}, show_mode=ShowMode.DELETE_AND_SEND)
    except (TelegramBadRequest, TelegramForbiddenError):
        logger.info(f"Failed to send messages to {user_id}, skip")


@broker.task()
@inject
async def delete_message(
    message: Message,
    bot: FromDishka[Bot],
) -> None:
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except (TelegramBadRequest, TelegramForbiddenError):
        logger.info(f"Failed to delete message id={message.message_id}, skip")
