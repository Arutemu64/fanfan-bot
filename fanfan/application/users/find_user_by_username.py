from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import UserDTO
from fanfan.infrastructure.db.models import User


class FindUserByUsername:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __call__(self, username: str) -> UserDTO:
        user = await self.session.scalar(
            select(User)
            .where(func.lower(User.username) == username.lower().replace("@", ""))
            .limit(1)
        )
        if user:
            return user.to_dto()
        raise UserNotFound
