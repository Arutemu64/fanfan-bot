from fanfan.application.common.id_provider import IdProvider
from fanfan.core.models.user import FullUserModel, UserId


class StubIdProvider(IdProvider):
    def get_current_user_id(self) -> UserId:
        return UserId(0)

    async def get_current_user(self) -> FullUserModel:
        raise NotImplementedError
