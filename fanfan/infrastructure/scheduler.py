import json
import logging
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter
from arq import ArqRedis, Retry, create_pool
from redis.asyncio import Redis

from fanfan.application.dto.common import UserNotification
from fanfan.common.factory import create_bot
from fanfan.config import conf
from fanfan.infrastructure.redis import create_redis_client
from fanfan.presentation.tgbot.dialogs.widgets import DELETE_BUTTON


async def startup(ctx: dict):
    ctx["bot"] = create_bot()
    ctx["arq"] = await create_pool(conf.redis.get_pool_settings())
    ctx["redis"] = create_redis_client()


async def shutdown(ctx: dict):
    bot: Bot = ctx["bot"]
    redis: Redis = ctx["redis"]
    await bot.session.close()
    await redis.aclose()


async def send_notification(
    ctx: dict, notification: UserNotification, delivery_id: Optional[str] = None
) -> None:
    bot: Bot = ctx["bot"]
    arq: ArqRedis = ctx["arq"]
    try:
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
    except TelegramRetryAfter as e:
        logging.warning(f"Flood control, retrying after {e.retry_after}s...")
        raise Retry(defer=e.retry_after)
    if delivery_id:
        redis: Redis = ctx["redis"]
        await redis.lpush(
            delivery_id,
            json.dumps(
                {
                    "chat_id": message.chat.id,
                    "message_id": message.message_id,
                    "text": message.text or message.caption,
                }
            ),
        )
        await redis.expire(delivery_id, time=600)
    if notification.delete_after:
        await arq.enqueue_job(
            "delete_message",
            message.chat.id,
            message.message_id,
            _defer_by=notification.delete_after,
        )


async def delete_message(ctx: dict, chat_id: int, message_id: int):
    bot: Bot = ctx["bot"]
    try:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )
    except TelegramRetryAfter as e:
        logging.warning(f"Flood control, retrying after {e.retry_after}s...")
        raise Retry(defer=e.retry_after)


class WorkerSettings:
    functions = [send_notification, delete_message]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = conf.redis.get_pool_settings()
