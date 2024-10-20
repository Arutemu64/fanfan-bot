from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.application.common.interactor import Interactor
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import FullUserModel, UserId


class GetUserById(Interactor[UserId, FullUserModel]):
    def __init__(self, users_repo: UsersRepository) -> None:
        self.users_repo = users_repo

    async def __call__(self, user_id: UserId) -> FullUserModel:
        if user := await self.users_repo.get_user_by_id(user_id):
            return user
        raise UserNotFound
