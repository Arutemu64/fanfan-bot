from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from fanfan.infrastructure.db.uow import UnitOfWork


class UOWMiddleware(BaseMiddleware):
    """This middleware throw a Database class to handler"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with data["session_pool"]() as session:
            uow = UnitOfWork(session)
            data["uow"] = uow
            return await handler(event, data)
