import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from arq import ArqRedis, Retry, Worker

from fanfan.application.dto.common import UserNotification
from fanfan.common.factory import create_bot
from fanfan.presentation.tgbot.dialogs.widgets import DELETE_BUTTON


async def startup(ctx: dict):
    ctx["bot"] = create_bot()


async def shutdown(ctx: dict):
    bot: Bot = ctx["bot"]
    await bot.session.close()


async def send_notification(ctx: dict, notification: UserNotification):
    bot: Bot = ctx["bot"]
    try:
        await bot.send_message(
            chat_id=notification.user_id,
            text=notification.render_message_text(),
            reply_markup=DELETE_BUTTON.as_markup(),
        )
    except TelegramBadRequest:
        logging.warning(
            f"Can't send notification to user {notification.user_id}, skipping..."
        )
    except TelegramRetryAfter as e:
        logging.warning(f"Flood control, retrying after {e.retry_after}s...")
        raise Retry(defer=e.retry_after)


def create_worker(pool: ArqRedis) -> Worker:
    return Worker(
        redis_pool=pool,
        on_startup=startup,
        on_shutdown=shutdown,
        functions=[send_notification],
    )
