from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, ErrorEvent, Message

from src.cache import Cache


class CacheMiddleware(BaseMiddleware):
    """This middleware throw a Database class to handler"""

    def __init__(self, cache: Cache):
        self.cache = cache

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery, ErrorEvent],
        data: Dict[str, Any],
    ) -> Any:
        data["cache"] = self.cache
        return await handler(event, data)
