from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.core.dto.user import UserDTO
from fanfan.core.exceptions.users import UserNotFound


class ReadUserByUsername:
    def __init__(self, users_repo: UsersRepository) -> None:
        self.users_repo = users_repo

    async def __call__(self, username: str) -> UserDTO:
        if user := await self.users_repo.read_user_by_username(
            username.lower().replace("@", "")
        ):
            return user
        raise UserNotFound
