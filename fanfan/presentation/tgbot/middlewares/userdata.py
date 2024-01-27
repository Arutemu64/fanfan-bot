from typing import Any, Awaitable, Callable, Dict, Optional

import sentry_sdk
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from fanfan.application.dto.user import CreateUserDTO, UpdateUserDTO
from fanfan.application.exceptions.users import UserNotFound
from fanfan.application.services import ServicesHolder
from fanfan.application.services.user import UserService
from fanfan.common.enums import UserRole
from fanfan.config import conf
from fanfan.infrastructure.db.uow import UnitOfWork


class UserDataMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id: int = data["event_from_user"].id
        username: Optional[str] = data["event_from_user"].username
        # Sentry logging
        if conf.sentry.enabled:
            sentry_sdk.set_user(
                {
                    "id": user_id,
                    "username": username,
                }
            )
        # Getting user from DB
        uow: UnitOfWork = data["uow"]
        try:
            user = await UserService(uow).get_user_by_id(user_id)
        except UserNotFound:
            user = await UserService(uow).create_user(
                CreateUserDTO(
                    id=user_id,
                    username=username,
                )
            )
        services = ServicesHolder(uow, user)
        # Updating user data
        if user.username != username:
            user = await services.users.update_user(
                UpdateUserDTO(
                    id=user_id,
                    username=username,
                )
            )
        if user.username:
            if (
                user.username.lower() in conf.bot.admin_list
                and user.role != UserRole.ORG
            ):
                user = await services.users.update_user(
                    UpdateUserDTO(
                        id=user_id,
                        role=UserRole.ORG,
                    )
                )
        data["user"] = user
        data["services"] = services
        return await handler(event, data)
