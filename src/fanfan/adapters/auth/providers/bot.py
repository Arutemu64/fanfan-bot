import typing

from dishka.integrations.aiogram import AiogramMiddlewareData

from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.auth import AuthenticationError
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import UserData
from fanfan.core.vo.user import UserId

if typing.TYPE_CHECKING:
    from aiogram.types import User as TelegramUser


class BotIdProvider(IdProvider):
    def __init__(
        self,
        middleware_data: AiogramMiddlewareData,
        users_repo: UsersRepository,
    ):
        self.middleware_data = middleware_data
        self.users_repo = users_repo

    def is_system(self) -> bool:
        return False

    def get_current_user_id(self) -> UserId:
        user: TelegramUser | None = self.middleware_data.get("event_from_user")
        if user:
            return UserId(user.id)
        raise AuthenticationError

    async def get_user_data(self) -> UserData:
        if user := await self.users_repo.get_user_data(self.get_current_user_id()):
            return user
        raise UserNotFound
