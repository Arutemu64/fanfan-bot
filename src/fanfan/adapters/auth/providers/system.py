from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.auth import NoUserContextError
from fanfan.core.models.user import User


class SystemIdProvider(IdProvider):
    async def get_current_user(self) -> User:
        raise NoUserContextError
