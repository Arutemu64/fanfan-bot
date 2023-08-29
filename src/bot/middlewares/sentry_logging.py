from typing import Any, Awaitable, Callable, Dict, Union

import sentry_sdk
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message


class SentryLoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        sentry_sdk.set_user(
            {
                "id": data["event_from_user"].id,
                "username": data["event_from_user"].username,
            }
        )
        return await handler(event, data)
