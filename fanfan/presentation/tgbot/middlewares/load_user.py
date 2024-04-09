from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject
from dishka import AsyncContainer
from dishka.integrations.aiogram import CONTAINER_NAME

from fanfan.application.dto.user import FullUserDTO
from fanfan.application.holder import AppHolder
from fanfan.presentation.tgbot.handlers.commands import (
    update_user_commands,
)


class LoadUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        container: AsyncContainer = data[CONTAINER_NAME]
        user = await container.get(FullUserDTO)
        app = await container.get(AppHolder)

        # Update user commands
        await update_user_commands(
            bot=await container.get(Bot),
            user=user,
            settings=await app.settings.get_settings(),
        )

        data["user"] = user
        data["app"] = app
        return await handler(event, data)
