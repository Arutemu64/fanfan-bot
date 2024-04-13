from typing import List, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.application.dto.user import UserStats
from fanfan.common.enums import UserRole
from fanfan.infrastructure.db.repositories.repo import Repository

from ..models import Achievement, ReceivedAchievement, User, UserSettings


class UsersRepository(Repository[User]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=User, session=session)

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return await self.session.get(
            User,
            user_id,
            options=[
                joinedload(User.ticket),
                joinedload(User.settings),
                joinedload(User.permissions),
            ],
        )

    async def get_user_by_username(self, username: str) -> Optional[User]:
        query = (
            select(User)
            .where(func.lower(User.username) == username.lower().replace("@", ""))
            .limit(1)
        )
        query = query.options(
            joinedload(User.ticket),
            joinedload(User.settings),
            joinedload(User.permissions),
        )
        return await self.session.scalar(query)

    async def get_all_by_roles(self, roles: List[UserRole]) -> Sequence[User]:
        query = select(User).where(User.role.in_(roles))
        return (await self.session.scalars(query)).all()

    async def get_receive_all_announcements_users(self) -> Sequence[User]:
        query = select(User).where(
            User.settings.has(UserSettings.receive_all_announcements.is_(True))
        )
        return (await self.session.scalars(query)).all()

    async def get_user_stats(self, user_id: int) -> UserStats:
        received_count_query = (
            select(func.count(ReceivedAchievement.id))
            .where(ReceivedAchievement.user_id == user_id)
            .label("received")
        )
        achievements_count_query = select(func.count(Achievement.id)).label("total")
        query = select(received_count_query, achievements_count_query)
        result = ((await self.session.execute(query)).all())[0]
        return UserStats(
            user_id=user_id,
            achievements_count=result.received,
            total_achievements=result.total,
        )
