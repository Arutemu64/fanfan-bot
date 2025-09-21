from dishka.integrations.aiogram import AiogramMiddlewareData

from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.auth import AuthenticationError
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import User
from fanfan.core.vo.telegram import TelegramUserId


class BotIdProvider(IdProvider):
    def __init__(
        self,
        middleware_data: AiogramMiddlewareData,
        users_repo: UsersRepository,
    ):
        self.middleware_data = middleware_data
        self.users_repo = users_repo

    async def get_current_user(self) -> User:
        if tg_user := self.middleware_data.get("event_from_user"):
            tg_id = TelegramUserId(tg_user.id)
            if user := await self.users_repo.get_user_by_tg_id(tg_id):
                return user
            raise UserNotFound
        raise AuthenticationError
