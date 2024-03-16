from datetime import timedelta
from typing import Annotated, Optional

from aiogram import Bot
from aiogram.types import Message
from aiogram_dialog import BgManagerFactory, ShowMode
from dishka import AsyncContainer
from redis.asyncio import Redis
from taskiq import (
    Context,
    TaskiqDepends,
)
from taskiq.serializers import ORJSONSerializer
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from fanfan.application.dto.common import UserNotification
from fanfan.config import conf
from fanfan.presentation.tgbot.dialogs.widgets import DELETE_BUTTON

redis_async_result = RedisAsyncResultBackend(
    redis_url=conf.redis.build_connection_str(),
    result_ex_time=timedelta(hours=1).seconds,
)

broker = (
    ListQueueBroker(
        url=conf.redis.build_connection_str(),
    )
    .with_result_backend(redis_async_result)
    .with_serializer(ORJSONSerializer())
)


async def bot_dep(context: Annotated[Context, TaskiqDepends()]) -> Bot:
    container: AsyncContainer = context.state.container
    return await container.get(Bot)


async def redis_dep(context: Annotated[Context, TaskiqDepends()]) -> Redis:
    container: AsyncContainer = context.state.container
    return await container.get(Redis)


async def bgm_factory_dep(
    context: Annotated[Context, TaskiqDepends()]
) -> BgManagerFactory:
    container: AsyncContainer = context.state.container
    return await container.get(BgManagerFactory)


@broker.task()
async def send_notification(
    notification: UserNotification,
    context: Annotated[Context, TaskiqDepends()],
    bot: Annotated[Bot, TaskiqDepends(bot_dep)],
    redis: Annotated[Redis, TaskiqDepends(redis_dep)],
    dialog_bg_factory: Annotated[BgManagerFactory, TaskiqDepends(bgm_factory_dep)],
    delivery_id: Optional[str] = None,
) -> dict:
    if notification.image_id:
        message = await bot.send_photo(
            chat_id=notification.user_id,
            photo=str(notification.image_id),
            caption=notification.render_message_text(),
            reply_markup=DELETE_BUTTON.as_markup(),
        )
    else:
        message = await bot.send_message(
            chat_id=notification.user_id,
            text=notification.render_message_text(),
            reply_markup=DELETE_BUTTON.as_markup(),
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


@broker.task()
async def delete_message(
    message: Message,
    bot: Annotated[Bot, TaskiqDepends(bot_dep)],
) -> None:
    await bot.delete_message(message.chat.id, message.message_id)
