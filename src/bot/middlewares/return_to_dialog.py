import asyncio
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from aiogram_dialog import DialogManager


class ReturnToDialog(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        dialog_manager: DialogManager = data.get("dialog_manager")
        result = await handler(event, data)
        if (
            event.text != "/start" or event.text != "/menu"
        ):  # TODO Не знаю насколько хороший способ, подумать над этим ещё
            await asyncio.sleep(2)
            await dialog_manager.show()
