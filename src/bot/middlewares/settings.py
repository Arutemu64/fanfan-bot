from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from redis.asyncio.client import Redis

from src.redis.global_settings import GlobalSettings


class GlobalSettingsMiddleware(BaseMiddleware):
    """This middleware throw a GlobalSettings class to handler"""

    def __init__(self, redis: Redis):
        self.redis = redis

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        data["settings"] = GlobalSettings(self.redis)
        return await handler(event, data)
