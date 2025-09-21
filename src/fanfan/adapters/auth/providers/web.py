from fastapi import Request

from fanfan.adapters.auth.utils.token import JwtTokenProcessor
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.auth import AuthenticationError
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import User


class WebIdProvider(IdProvider):
    def __init__(
        self,
        request: Request,
        token_processor: JwtTokenProcessor,
        users_repo: UsersRepository,
    ):
        self.request = request
        self.token_processor = token_processor
        self.users_repo = users_repo

    async def get_current_user(self) -> User:
        if token := self.request.session.get("token"):
            user_id = self.token_processor.validate_token(token)
            if user := await self.users_repo.get_user_by_id(user_id):
                return user
            raise UserNotFound
        raise AuthenticationError
