from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from redis.asyncio.client import Redis

from src.bot.structures import Settings


class SettingsMiddleware(BaseMiddleware):
    """This middleware throw a Settings class to handler"""

    def __init__(self, redis: Redis):
        self.redis = redis

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        data["settings"] = Settings(self.redis)
        return await handler(event, data)
