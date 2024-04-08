from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from dishka import AsyncContainer
from dishka.integrations.aiogram import CONTAINER_NAME

from fanfan.application.dto.user import FullUserDTO
from fanfan.application.holder import AppHolder


class LoadUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        container: AsyncContainer = data[CONTAINER_NAME]
        data["user"] = await container.get(FullUserDTO)
        data["app"] = await container.get(AppHolder)
        return await handler(event, data)
