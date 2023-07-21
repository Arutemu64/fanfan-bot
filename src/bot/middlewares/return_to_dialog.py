import asyncio
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from aiogram_dialog import DialogManager


class ReturnToDialog(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        dialog_manager: DialogManager = data.get("dialog_manager")
        await handler(event, data)
        if (
            event.text != "/start" or event.text != "/menu"
        ):  # TODO Не знаю насколько хороший способ, подумать над этим ещё
            await asyncio.sleep(1)
            await dialog_manager.update(data=dialog_manager.dialog_data)
