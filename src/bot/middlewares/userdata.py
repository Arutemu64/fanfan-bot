from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, ErrorEvent, Message, TelegramObject

from src.db import Database
from src.db.models import User


class UserData(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery, ErrorEvent],
        data: Dict[str, Any],
    ) -> Any:
        db: Database = data["db"]
        if type(event) is ErrorEvent:
            if event.update.message:
                user = await db.user.get_by_where(
                    User.tg_id == event.update.message.from_user.id
                )
            elif event.update.callback_query:
                user = await db.user.get_by_where(
                    User.tg_id == event.update.callback_query.from_user.id
                )
        else:
            user = await db.user.get_by_where(User.tg_id == data["event_from_user"].id)
        data["user"] = user
        return await handler(event, data)
