import asyncio
import logging

from aiogram import Bot
from aiogram.client.session.middlewares.base import (
    BaseRequestMiddleware,
    NextRequestMiddlewareType,
)
from aiogram.exceptions import TelegramRetryAfter
from aiogram.methods.base import Response, TelegramMethod, TelegramType


class RetryMiddleware(BaseRequestMiddleware):
    async def __call__(
        self,
        make_request: NextRequestMiddlewareType[TelegramType],
        bot: Bot,
        method: TelegramMethod[TelegramType],
    ) -> Response[TelegramType]:
        while True:
            try:
                return await make_request(bot, method)
            except TelegramRetryAfter as e:
                logging.info(f"Too many requests, retrying in {e.retry_after}")
                await asyncio.sleep(e.retry_after)
