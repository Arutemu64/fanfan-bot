from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.application.common.interactor import Interactor
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import UserModel


class GetUserByUsername(Interactor[str, UserModel]):
    def __init__(self, users_repo: UsersRepository) -> None:
        self.users_repo = users_repo

    async def __call__(self, username: str) -> UserModel:
        if user := await self.users_repo.get_user_by_username(
            username.lower().replace("@", "")
        ):
            return user
        raise UserNotFound