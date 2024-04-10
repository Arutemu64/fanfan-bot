from datetime import timedelta
from typing import Annotated, Optional

from aiogram import Bot
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import BgManagerFactory, ShowMode
from dishka import FromDishka
from dishka.integrations.taskiq import inject
from redis.asyncio import Redis
from taskiq import (
    Context,
    TaskiqDepends,
)
from taskiq.serializers import ORJSONSerializer
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from fanfan.application.dto.notification import UserNotification
from fanfan.config import get_config
from fanfan.presentation.tgbot.dialogs.widgets import DELETE_BUTTON

redis_async_result = RedisAsyncResultBackend(
    redis_url=get_config().redis.build_connection_str(),
    result_ex_time=timedelta(hours=1).seconds,
)

broker = (
    ListQueueBroker(
        url=get_config().redis.build_connection_str(),
    )
    .with_result_backend(redis_async_result)
    .with_serializer(ORJSONSerializer())
)


@broker.task
@inject
async def send_notification(
    notification: UserNotification,
    context: Annotated[Context, TaskiqDepends()],
    bot: FromDishka[Bot],
    redis: FromDishka[Redis],
    dialog_bg_factory: FromDishka[BgManagerFactory],
    delivery_id: Optional[str] = None,
) -> dict:
    if notification.image_id:
        message = await bot.send_photo(
            chat_id=notification.user_id,
            photo=str(notification.image_id),
            caption=notification.render_message_text(),
            reply_markup=InlineKeyboardBuilder([[DELETE_BUTTON]]).as_markup(),
        )
    else:
        message = await bot.send_message(
            chat_id=notification.user_id,
            text=notification.render_message_text(),
            reply_markup=InlineKeyboardBuilder([[DELETE_BUTTON]]).as_markup(),
        )
    await dialog_bg_factory.bg(
        bot=bot,
        user_id=notification.user_id,
        chat_id=notification.user_id,
        load=True,
    ).update(data={}, show_mode=ShowMode.DELETE_AND_SEND)
    if delivery_id:
        await redis.lpush(delivery_id, context.message.task_id)
        await redis.expire(delivery_id, time=timedelta(hours=1).seconds)
    return message.model_dump(mode="json", exclude_none=True)


@broker.task
@inject
async def delete_message(
    message: Message,
    bot: FromDishka[Bot],
) -> None:
    await bot.delete_message(message.chat.id, message.message_id)
