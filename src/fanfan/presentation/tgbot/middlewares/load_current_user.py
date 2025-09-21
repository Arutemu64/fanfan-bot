from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, Final

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from dishka.integrations.aiogram import CONTAINER_NAME
from opentelemetry import trace
from structlog.contextvars import bind_contextvars

from fanfan.application.users.tg_authenticate import TgAuthenticate, TgAuthenticateDTO
from fanfan.core.dto.user import FullUserDTO

if TYPE_CHECKING:
    from aiogram.types import User
    from dishka import AsyncContainer

tracer = trace.get_tracer(__name__)
CURRENT_USER_KEY: Final[str] = "current_user"


def inject_current_user(middleware_data: dict, current_user: FullUserDTO):
    middleware_data[CURRENT_USER_KEY] = current_user


class LoadCurrentUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if data.get("event_from_user"):
            tg_user: User = data["event_from_user"]
            trace_msg = f"User {tg_user.id} (@{tg_user.username}) action"
            with tracer.start_as_current_span(trace_msg) as span:
                span.set_attribute("user_id", tg_user.id)

                # Logging
                bind_contextvars(user_id=tg_user.id)

                container: AsyncContainer = data[CONTAINER_NAME]
                authenticate = await container.get(TgAuthenticate)

                # Authenticate
                current_user = await authenticate(
                    TgAuthenticateDTO.from_aiogram(tg_user)
                )

                # DI
                inject_current_user(data, current_user)

                return await handler(event, data)

        return await handler(event, data)
