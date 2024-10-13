from adaptix import Retort
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, undefer

from fanfan.core.enums import UserRole
from fanfan.core.models.quest import QuestParticipantDTO
from fanfan.core.models.user import (
    FullUserModel,
    UserId,
    UserModel,
    UserSettingsModel,
)
from fanfan.infrastructure.db.models import User, UserSettings


class UsersRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user(self, model: UserModel) -> UserModel:
        user = User(id=model.id, username=model.username, role=model.role)
        self.session.add(user)
        await self.session.flush([user])
        return user.to_model()

    async def get_user_by_id(
        self,
        user_id: UserId,
    ) -> FullUserModel | None:
        user = await self.session.get(
            User,
            user_id,
            options=[
                joinedload(User.ticket),
                joinedload(User.settings),
                joinedload(User.permissions),
            ],
            # populate_existing=True,  #noqa: ERA001
        )
        return user.to_full_model() if user else None

    async def get_user_for_quest(self, user_id: UserId) -> QuestParticipantDTO | None:
        query = (
            select(User)
            .where(User.id == user_id)
            .options(
                joinedload(User.ticket),
                joinedload(User.quest_registration),
                undefer(User.achievements_count),
                undefer(User.points),
            )
        )
        user = await self.session.scalar(query)
        return (
            QuestParticipantDTO(
                id=UserId(user.id),
                points=user.points,
                achievements_count=user.achievements_count,
                quest_registration=bool(user.quest_registration),
                ticket=user.ticket.to_model() if user.ticket else None,
            )
            if user
            else None
        )

    async def get_user_by_username(self, username: str) -> UserModel | None:
        user = await self.session.scalar(
            select(User).where(func.lower(User.username) == username).limit(1)
        )
        return user.to_model() if user else None

    async def get_all_by_roles(self, *roles: UserRole) -> list[UserModel]:
        users = await self.session.scalars(select(User).where(User.role.in_(roles)))
        return [u.to_model() for u in users]

    async def get_users_by_receive_all_announcements(self) -> list[UserModel]:
        users = await self.session.scalars(
            select(User).where(
                User.settings.has(UserSettings.receive_all_announcements.is_(True))
            )
        )
        return [u.to_model() for u in users]

    async def update_user(self, model: UserModel) -> None:
        retort = Retort()
        user = User(**retort.dump(model))
        await self.session.merge(user)

    async def update_user_settings(self, model: UserSettingsModel) -> None:
        retort = Retort()
        settings = UserSettings(**retort.dump(model))
        await self.session.merge(settings)

    async def add_points(self, user_id: UserId, points: int) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(points=User.points + points)
        )
