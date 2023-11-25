import logging

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from arq import ArqRedis, Retry, Worker

from src.bot.dialogs.widgets import DELETE_BUTTON
from src.bot.structures import Notification
from src.config import conf


async def startup(ctx: dict):
    ctx["bot"] = Bot(token=conf.bot.token, parse_mode=ParseMode.HTML)


async def shutdown(ctx: dict):
    bot: Bot = ctx["bot"]
    await bot.session.close()


async def send_notification(ctx: dict, notification: Notification):
    bot: Bot = ctx["bot"]
    try:
        await bot.send_message(
            chat_id=notification.user_id,
            text=f"<b>📢 УВЕДОМЛЕНИЕ</b>\n\n{notification.text}",
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
