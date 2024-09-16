from __future__ import annotations

from typing import TYPE_CHECKING, Any

import sentry_sdk
from aiogram import BaseMiddleware
from dishka.integrations.aiogram import CONTAINER_NAME

from fanfan.application.users.create_user import CreateUser, CreateUserDTO
from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.application.users.update_user import UpdateUser, UpdateUserDTO
from fanfan.application.users.update_user_commands import UpdateUserCommands
from fanfan.common.config import DebugConfig
from fanfan.core.exceptions.users import UserNotFound

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import TelegramObject, User
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
            create_user = await container.get(CreateUser)
            update_user = await container.get(UpdateUser)
            get_user_by_id = await container.get(GetUserById)
            update_user_commands = await container.get(UpdateUserCommands)

            # Setup Sentry logging
            debug_config = await container.get(DebugConfig)
            if debug_config.sentry_enabled:
                sentry_sdk.set_user(
                    {
                        "id": tg_user.id,
                        "username": tg_user.username,
                    },
                )

            # Check if user exists, create if not
            try:
                user = await get_user_by_id(tg_user.id)
            except UserNotFound:
                await create_user(
                    CreateUserDTO(
                        id=tg_user.id,
                        username=tg_user.username,
                    ),
                )
                user = await get_user_by_id(tg_user.id)

            # Update username in database
            if user.username != tg_user.username:
                await update_user(
                    UpdateUserDTO(
                        id=tg_user.id,
                        username=tg_user.username,
                    ),
                )
                user = await get_user_by_id(tg_user.id)

            # Update user commands
            await update_user_commands(user_id=tg_user.id)

            # DI
            data["user"] = user
            data["container"] = container

        return await handler(event, data)
