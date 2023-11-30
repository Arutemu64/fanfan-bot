from typing import Optional, Sequence

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.structures import UserRole

from ..models import DBUser
from .abstract import Repository


class UserRepo(Repository[DBUser]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=DBUser, session=session)

    async def new(
        self,
        id: int,
        username: Optional[str] = None,
        role: UserRole = UserRole.VISITOR,
    ) -> DBUser:
        new_user = await self.session.merge(
            DBUser(
                id=id,
                username=username,
                role=role,
            )
        )
        return new_user

    async def get(self, user_id: int) -> Optional[DBUser]:
        return await super()._get(ident=user_id)

    async def get_by_username(self, username: str) -> Optional[DBUser]:
        username = username.replace("@", "").lower()
        return await super()._get_by_where(func.lower(DBUser.username) == username)

    async def get_receive_all_announcements_users(self) -> Sequence[DBUser]:
        return await super()._get_many(
            DBUser.receive_all_announcements.is_(True),
        )

    async def get_by_role(self, role: UserRole) -> Sequence[DBUser]:
        return await super()._get_many(DBUser.role == role)
