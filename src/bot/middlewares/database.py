from typing import Any, Awaitable, Callable, Dict, Union

import sentry_sdk
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from aiogram_dialog.api.entities import DialogUpdate

from src.db.database import Database


class DatabaseMiddleware(BaseMiddleware):
    """This middleware throw a Database class to handler"""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery, DialogUpdate],
        data: Dict[str, Any],
    ) -> Any:
        async with data["session_pool"]() as session:
            with sentry_sdk.start_transaction(name="DatabaseTransaction"):
                db = Database(session)
                data["db"] = db
                return await handler(event, data)
