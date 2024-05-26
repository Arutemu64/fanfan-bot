from typing import List, Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.application.dto.user import (
    CreateUserDTO,
    FullUserDTO,
    UpdateUserDTO,
    UserDTO,
    UserStats,
)
from fanfan.common.enums import UserRole
from fanfan.infrastructure.db.repositories.repo import Repository

from ..models import (
    Achievement,
    ReceivedAchievement,
    User,
    UserPermissions,
    UserSettings,
)


class UsersRepository(Repository[User]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=User, session=session)

    async def add_user(self, dto: CreateUserDTO) -> UserDTO:
        user = User(
            id=dto.id,
            username=dto.username,
            role=dto.role,
            settings=UserSettings(),
            permissions=UserPermissions(),
        )
        self.session.add(user)
        await self.session.flush([user])
        return user.to_dto()

    async def get_user_by_id(self, user_id: int) -> Optional[FullUserDTO]:
        user = await self.session.get(
            User,
            user_id,
            options=[
                joinedload(User.ticket),
                joinedload(User.settings),
                joinedload(User.permissions),
            ],
        )
        return user.to_full_dto() if user else None

    async def get_user_by_username(self, username: str) -> Optional[FullUserDTO]:
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
        user = await self.session.scalar(query)
        return user.to_full_dto() if user else None

    async def get_all_by_roles(self, roles: List[UserRole]) -> List[UserDTO]:
        query = select(User).where(User.role.in_(roles))
        return [user.to_dto() for user in (await self.session.scalars(query)).all()]

    async def get_receive_all_announcements_users(self) -> List[UserDTO]:
        query = select(User).where(
            User.settings.has(UserSettings.receive_all_announcements.is_(True))
        )
        return [user.to_dto() for user in (await self.session.scalars(query)).all()]

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

    async def update_user(self, dto: UpdateUserDTO) -> None:
        await self.session.execute(
            update(User)
            .where(User.id == dto.id)
            .values(**dto.model_dump(exclude_unset=True, exclude={"id", "settings"}))
        )
        if dto.settings:
            await self.session.execute(
                update(UserSettings)
                .where(UserSettings.user_id == dto.id)
                .values(**dto.settings.model_dump(exclude_unset=True))
            )
        return None
