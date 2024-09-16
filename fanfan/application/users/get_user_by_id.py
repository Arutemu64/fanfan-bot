from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import FullUserDTO
from fanfan.infrastructure.db.models import User


class GetUserById:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __call__(self, user_id: int) -> FullUserDTO:
        user = await self.session.get(
            User,
            user_id,
            options=[
                joinedload(User.ticket),
                joinedload(User.settings),
                joinedload(User.permissions),
            ],
        )
        if user:
            return user.to_full_dto()
        raise UserNotFound
