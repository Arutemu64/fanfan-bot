from typing import List, Optional

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import undefer

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

    async def exists(
        self, user_id: Optional[int] = None, username: Optional[str] = None
    ) -> Optional[int]:
        query = None
        if user_id:
            query = User.id == user_id
        elif username:
            query = func.lower(User.username) == username.lower()
        return await super()._exists(query)

    async def get(
        self,
        user_id: User.id,
        load_achievements_count: bool = False,
    ) -> Optional[User]:
        return await super()._get(
            ident=user_id,
            options=[undefer(User.achievements_count)]
            if load_achievements_count
            else None,
        )

    async def get_role(self, user_id: int) -> UserRole:
        return await self.session.scalar(
            select(User.role).where(User.id == user_id).limit(1)
        )

    async def change_role(self, user_id: int, role: UserRole):
        stmt = update(User).where(User.id == user_id).values(role=role)
        await self.session.execute(stmt)

    async def get_items_per_page(self, user_id: int) -> int:
        return await self.session.scalar(
            select(User.items_per_page).where(User.id == user_id).limit(1)
        )

    async def set_items_per_page(self, user_id: int, value: int):
        stmt = update(User).where(User.id == user_id).values(items_per_page=value)
        await self.session.execute(stmt)

    async def set_receive_all_announcements(self, user_id: int, value: bool):
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(receive_all_announcements=value)
        )
        await self.session.execute(stmt)

    async def set_points(self, user_id: int, points: int):
        await self.session.execute(
            update(User).where(User.id == user_id).values(points=points)
        )

    async def add_points(self, user_id: int, points: int):
        user_points = await self.session.scalar(
            select(User.points).where(User.id == user_id).limit(1)
        )
        await self.set_points(user_id, user_points + points)

    async def get_receive_all_announcements_user_ids(self) -> List[int]:
        result = (
            await self.session.execute(
                select(User.id).where(User.receive_all_announcements.is_(True))
            )
        ).all()
        return [r[0] for r in result]

    async def get_count(self, role: UserRole = None) -> int:
        terms = []
        if role is not None:
            terms.append(User.role == role)
        return await super()._get_count(query=and_(*terms))

    async def update_username(self, user_id: int, username: str):
        stmt = update(User).where(User.id == user_id).values(username=username)
        await self.session.execute(stmt)
