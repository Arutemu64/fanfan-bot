from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.auth import NoUserContextError
from fanfan.core.models.user import UserData
from fanfan.core.vo.user import UserId


class SystemIdProvider(IdProvider):
    def is_system(self) -> bool:
        return True

    def get_current_user_id(self) -> UserId:
        raise NoUserContextError

    async def get_user_data(self) -> UserData:
        raise NoUserContextError
