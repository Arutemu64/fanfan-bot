from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from dishka.integrations.aiogram import CONTAINER_NAME
from opentelemetry import trace
from structlog.contextvars import bind_contextvars

from fanfan.application.users.authenticate import Authenticate, AuthenticateDTO
from fanfan.presentation.tgbot.utils.cmd_updater import CMDUpdater

if TYPE_CHECKING:
    from aiogram.types import User
    from dishka import AsyncContainer

tracer = trace.get_tracer(__name__)


class LoadDataMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        with tracer.start_as_current_span("User action") as span:
            if data.get("event_from_user"):
                tg_user: User = data["event_from_user"]
                span.set_attribute("user_id", tg_user.id)

                # Logging
                bind_contextvars(user_id=tg_user.id)

                container: AsyncContainer = data[CONTAINER_NAME]
                authenticate: Authenticate = await container.get(Authenticate)
                update_user_commands: CMDUpdater = await container.get(CMDUpdater)

                # Authenticate
                user = await authenticate(AuthenticateDTO.from_aiogram(tg_user))

                # Update user commands
                await update_user_commands()

                # DI
                data["user"] = user
                data["container"] = container

            return await handler(event, data)
