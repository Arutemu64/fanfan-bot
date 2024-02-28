from datetime import timedelta
from typing import Annotated, Optional

from aiogram import Bot
from aiogram_dialog import BgManagerFactory, ShowMode
from redis.asyncio import ConnectionPool, Redis
from taskiq import (
    Context,
    TaskiqDepends,
    TaskiqEvents,
    TaskiqState,
)
from taskiq.serializers import ORJSONSerializer
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from fanfan.application.dto.common import UserNotification
from fanfan.common.factory import create_bot
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


def bot_dep(context: Annotated[Context, TaskiqDepends()]) -> Bot:
    return context.state.bot


def redis_dep(context: Annotated[Context, TaskiqDepends()]) -> Redis:
    return Redis(connection_pool=context.state.redis_pool, decode_responses=True)


def bgm_factory_dep(context: Annotated[Context, TaskiqDepends()]) -> BgManagerFactory:
    return context.state.dialog_bg_factory


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    state.bot = create_bot()
    state.redis_pool = ConnectionPool.from_url(conf.redis.build_connection_str())


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(state: TaskiqState) -> None:
    bot: Bot = state.bot
    pool: ConnectionPool = state.redis_pool
    await bot.session.close()
    await pool.aclose()


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
    return {
        "chat_id": message.chat.id,
        "message_id": message.message_id,
        "text": message.text or message.caption,
        "image_id": notification.image_id,
    }


@broker.task()
async def delete_message(
    chat_id: int,
    message_id: int,
    bot: Annotated[Bot, TaskiqDepends(bot_dep)],
) -> None:
    await bot.delete_message(chat_id, message_id)
