from __future__ import annotations

from typing import TYPE_CHECKING, Any

import sentry_sdk
from aiogram import BaseMiddleware
from dishka.integrations.aiogram import CONTAINER_NAME
from opentelemetry import trace

from fanfan.adapters.config_reader import DebugConfig
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.users.authenticate import Authenticate, AuthenticateDTO
from fanfan.application.users.update_user import UpdateUser, UpdateUserDTO
from fanfan.application.users.update_user_commands import UpdateUserCommands
from fanfan.core.models.user import UserId

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import TelegramObject, User
    from dishka import AsyncContainer

tracer = trace.get_tracer(__name__)


class LoadDataMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        with tracer.start_as_current_span("user action"):
            if data.get("event_from_user"):
                tg_user: User = data["event_from_user"]
                container: AsyncContainer = data[CONTAINER_NAME]
                id_provider: IdProvider = await container.get(IdProvider)
                authenticate: Authenticate = await container.get(Authenticate)
                update_user: UpdateUser = await container.get(UpdateUser)
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
                user = await authenticate(
                    AuthenticateDTO(id=UserId(tg_user.id), username=tg_user.username)
                )

                # Update username in database
                if user.username != tg_user.username:
                    await update_user(
                        UpdateUserDTO(id=user.id, username=tg_user.username)
                    )
                    user = await id_provider.get_current_user()

                # Update user commands
                await update_user_commands()

                # DI
                data["user"] = user
                data["container"] = container

            return await handler(event, data)
