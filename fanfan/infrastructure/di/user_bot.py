import sentry_sdk
from aiogram.types import TelegramObject, User
from dishka import Provider, Scope, from_context, provide

from fanfan.application.dto.user import CreateUserDTO, FullUserDTO, UpdateUserDTO
from fanfan.application.exceptions.users import UserNotFound
from fanfan.application.holder import AppHolder
from fanfan.application.services import UserService
from fanfan.common.enums import UserRole
from fanfan.config import BotConfig, DebugConfig
from fanfan.infrastructure.db import UnitOfWork


class UserProvider(Provider):
    scope = Scope.REQUEST

    telegram_object = from_context(
        provides=TelegramObject,
        scope=Scope.REQUEST,
    )

    @provide
    async def get_current_telegram_user(self, request: TelegramObject) -> User:
        return request.event.from_user

    @provide
    async def get_current_user(
        self,
        tg_user: User,
        uow: UnitOfWork,
        bot_config: BotConfig,
        debug_config: DebugConfig,
    ) -> FullUserDTO:
        if debug_config.sentry_enabled:
            sentry_sdk.set_user(
                {
                    "id": tg_user.id,
                    "username": tg_user.username,
                },
            )
        # Getting user from DB
        try:
            user = await UserService(uow).get_user_by_id(tg_user.id)
        except UserNotFound:
            user = await UserService(uow).create_user(
                CreateUserDTO(
                    id=tg_user.id,
                    username=tg_user.username,
                ),
            )
        services = AppHolder(uow, user)
        # Updating user data
        if user.username != tg_user.username:
            user = await services.users.update_user(
                UpdateUserDTO(
                    id=tg_user.id,
                    username=tg_user.username,
                ),
            )
        if user.username:
            if (
                user.username.lower() in bot_config.admin_list
                and user.role != UserRole.ORG
            ):
                user = await services.users.update_user(
                    UpdateUserDTO(
                        id=tg_user.id,
                        role=UserRole.ORG,
                    ),
                )
        return user

    @provide
    async def get_app_holder(
        self,
        uow: UnitOfWork,
        identity: FullUserDTO,
    ) -> AppHolder:
        return AppHolder(uow, identity)
