from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.user import FullUserDTO


class GetCurrentUser:
    def __init__(self, users_repo: UsersRepository, id_provider: IdProvider) -> None:
        self.users_repo = users_repo
        self.id_provider = id_provider

    async def __call__(self) -> FullUserDTO:
        current_user = await self.id_provider.get_current_user()
        return await self.users_repo.read_user_by_id(current_user.id)
