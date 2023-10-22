from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import defer

from src.bot.structures import UserRole

from ..models import User
from .abstract import Repository


class UserRepo(Repository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=User, session=session)

    async def new(
        self,
        id: Optional[int] = None,
        username: Optional[str] = None,
        role: UserRole = UserRole.VISITOR,
    ) -> User:
        new_user = await self.session.merge(
            User(
                id=id,
                username=username,
                role=role,
            )
        )
        return new_user

    async def get(self, user_id: int) -> Optional[User]:
        return await super()._get(ident=user_id)

    async def get_by_username(self, username: str) -> Optional[User]:
        username = username.replace("@", "").lower()
        return await super()._get_by_where(func.lower(User.username) == username)

    async def get_receive_all_announcements_users(self) -> List[User]:
        return await super()._get_many(
            User.receive_all_announcements.is_(True),
            options=[defer(User.achievements_count)],
        )
