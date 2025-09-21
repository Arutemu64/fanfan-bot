from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.core.dto.user import FullUserDTO
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.vo.user import UserId


class GetUserById:
    def __init__(self, users_repo: UsersRepository) -> None:
        self.users_repo = users_repo

    async def __call__(self, user_id: UserId) -> FullUserDTO:
        if user := await self.users_repo.read_user_by_id(user_id):
            return user
        raise UserNotFound
