from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.auth import NoAuthenticationRequired
from fanfan.core.models.user import FullUserModel, UserId


class StubIdProvider(IdProvider):
    def get_current_user_id(self) -> UserId:
        raise NoAuthenticationRequired

    async def get_current_user(self) -> FullUserModel:
        raise NoAuthenticationRequired
