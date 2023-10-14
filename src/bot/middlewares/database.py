from typing import Any, Awaitable, Callable, Dict, Union

import sentry_sdk
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import conf
from src.db.database import Database, create_async_engine


class DatabaseMiddleware(BaseMiddleware):
    """This middleware throw a Database class to handler"""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        async with AsyncSession(
            bind=data.get("engine")
            or create_async_engine(conf.db.build_connection_str()),
            expire_on_commit=False,
        ) as session:
            with sentry_sdk.start_transaction(name="DatabaseMiddleware"):
                data["db"] = Database(session)
                return await handler(event, data)
