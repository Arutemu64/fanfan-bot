from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

import sentry_sdk
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from dishka.integrations.aiogram import CONTAINER_NAME

from fanfan.adapters.config.models import DebugConfig
from fanfan.application.users.authenticate import Authenticate, AuthenticateDTO
from fanfan.application.users.update_user_commands import UpdateUserCommands

if TYPE_CHECKING:
    from aiogram.types import User
    from dishka import AsyncContainer


class LoadDataMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if data.get("event_from_user"):
            tg_user: User = data["event_from_user"]
            container: AsyncContainer = data[CONTAINER_NAME]
            authenticate: Authenticate = await container.get(Authenticate)
            update_user_commands: UpdateUserCommands = await container.get(
                UpdateUserCommands
            )

            # Setup Sentry logging
            debug_config: DebugConfig = await container.get(DebugConfig)
            if debug_config.sentry_enabled:
                sentry_sdk.set_user(
                    {
                        "id": tg_user.id,
                        "username": tg_user.username,
                    },
                )

            # Authenticate
            user = await authenticate(AuthenticateDTO.from_aiogram(tg_user))

            # Update user commands
            await update_user_commands()

            # DI
            data["user"] = user
            data["container"] = container

        return await handler(event, data)
