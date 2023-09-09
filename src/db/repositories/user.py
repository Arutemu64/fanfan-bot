from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.structures import UserRole

from ..models import User
from .abstract import Repository


class UserRepo(Repository[User]):
    """
    User repository for CRUD and other SQL queries
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize user repository as for all users or only for one user
        """
        super().__init__(type_model=User, session=session)

    async def new(
        self,
        id: int = None,
        username: str = None,
        role: str = UserRole.VISITOR,
    ) -> User:
        new_user = await self.session.merge(
            User(
                id=id,
                username=username,
                role=role,
            )
        )
        return new_user

    async def exists(
        self, user_id: Optional[int] = None, username: Optional[str] = None
    ) -> Optional[int]:
        stmt = select(User.id)
        if user_id:
            stmt = stmt.where(User.id == user_id)
        elif username:
            stmt = stmt.where(func.lower(User.username) == username.lower())
        stmt = stmt.limit(1)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_role(self, user_id: int) -> str:
        return await self.session.scalar(
            select(User.role).where(User.id == user_id).limit(1)
        )

    async def get_items_per_page_setting(self, user_id: int) -> int:
        return await self.session.scalar(
            select(User.items_per_page).where(User.id == user_id).limit(1)
        )

    async def set_items_per_page_setting(self, user_id: int, value: int):
        await self.session.execute(
            update(User).where(User.id == user_id).values(items_per_page=value)
        )
        await self.session.commit()

    async def get_receive_all_announcements_setting(self, user_id: int) -> bool:
        return await self.session.scalar(
            select(User.receive_all_announcements).where(User.id == user_id).limit(1)
        )

    async def toggle_receive_all_announcements(self, user_id: int):
        await self.session.execute(
            update(User.receive_all_announcements)
            .where(User.id == user_id)
            .values(
                receive_all_announcements=not await self.get_receive_all_announcements_setting(  # noqa: E501
                    user_id
                )
            )
        )
        await self.session.commit()

    async def add_points(self, user_id: int, points: int):
        user_points = await self.session.scalar(
            select(User.points).where(User.id == user_id).limit(1)
        )
        await self.session.execute(
            update(User).where(User.id == user_id).values(points=user_points + points)
        )

    async def set_points(self, user_id: int, points: int):
        await self.session.execute(
            update(User).where(User.id == user_id).values(points=points)
        )
