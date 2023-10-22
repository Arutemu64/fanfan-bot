import asyncio
import logging
from asyncio import Queue
from dataclasses import dataclass

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter

from src.bot.dialogs.widgets import DELETE_BUTTON


@dataclass
class Notification:
    user_id: int
    text: str


queue = Queue()


async def queue_worker(bot: Bot):
    while True:
        notification: Notification = await queue.get()
        try:
            await bot.send_message(
                chat_id=notification.user_id,
                text=f"<b>📢 ПЕРСОНАЛЬНОЕ УВЕДОМЛЕНИЕ</b>\n{notification.text}",
                reply_markup=DELETE_BUTTON.as_markup(),
            )
        except TelegramBadRequest:
            logging.warning(
                f"Can't send notification to user {notification.user_id}, skipping..."
            )
        except TelegramRetryAfter as error:
            logging.warning(f"Flood control, retrying after {error.retry_after}s...")
            await queue.put(notification)
            await asyncio.sleep(error.retry_after)
