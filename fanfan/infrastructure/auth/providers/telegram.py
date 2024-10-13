from aiogram.dispatcher.middlewares.user_context import UserContextMiddleware
from aiogram.types import (
    CallbackQuery,
    ErrorEvent,
    InlineQuery,
    Message,
    TelegramObject,
)
from aiogram_dialog.api.entities import DialogUpdate

from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.auth import AuthenticationError
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import FullUserModel, UserId
from fanfan.infrastructure.db.repositories.users import UsersRepository


class TelegramIdProvider(IdProvider):
    def __init__(
        self,
        obj: TelegramObject,
        users_repo: UsersRepository,
    ):
        self.obj = obj
        self.users_repo = users_repo

    def get_current_user_id(self) -> UserId:
        if (
            isinstance(self.obj, (Message | CallbackQuery | InlineQuery))
            and self.obj.from_user
        ):
            return UserId(self.obj.from_user.id)
        if isinstance(self.obj, DialogUpdate):
            return UserId(self.obj.event.from_user.id)
        if isinstance(self.obj, ErrorEvent):
            context = UserContextMiddleware.resolve_event_context(self.obj.update)
            return UserId(context.user_id)
        raise AuthenticationError

    async def get_current_user(self) -> FullUserModel:
        if user := await self.users_repo.get_user_by_id(self.get_current_user_id()):
            return user
        raise UserNotFound
