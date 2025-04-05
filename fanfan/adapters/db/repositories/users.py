from sqlalchemy import Select, and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.adapters.db.models import UserORM, UserPermissionsORM, UserSettingsORM
from fanfan.core.models.user import (
    User,
    UserFull,
    UserId,
    UserRole,
)
from fanfan.core.models.user_settings import UserSettings


class UsersRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _load_full(query: Select) -> Select:
        return query.options(
            joinedload(UserORM.ticket),
            joinedload(UserORM.settings),
            joinedload(UserORM.permissions),
        )

    async def save_user(self, model: User) -> User:
        user = await self.session.merge(UserORM.from_model(model))
        await self.session.flush([user])
        return user.to_model()

    async def get_user_by_id(
        self,
        user_id: UserId,
    ) -> UserFull | None:
        query = (
            select(UserORM)
            .where(UserORM.id == user_id)
            .execution_options(populate_existing=True)
        )
        query = self._load_full(query)
        user = await self.session.scalar(query)
        return user.to_full_model() if user else None

    async def get_user_by_username(self, username: str) -> User | None:
        user = await self.session.scalar(
            select(UserORM).where(func.lower(UserORM.username) == username).limit(1)
        )
        return user.to_model() if user else None

    async def get_all_by_roles(self, *roles: UserRole) -> list[User]:
        users = await self.session.scalars(
            select(UserORM).where(UserORM.role.in_(roles))
        )
        return [u.to_model() for u in users]

    async def get_users_by_receive_all_announcements(self) -> list[User]:
        users = await self.session.scalars(
            select(UserORM).where(
                UserORM.settings.has(
                    UserSettingsORM.receive_all_announcements.is_(True)
                )
            )
        )
        return [u.to_model() for u in users]

    async def get_orgs_for_feedback_notification(self) -> list[User]:
        orgs = await self.session.scalars(
            select(UserORM).where(
                and_(
                    UserORM.role == UserRole.ORG,
                    UserORM.settings.has(
                        UserSettingsORM.org_receive_feedback_notifications.is_(True)
                    ),
                )
            )
        )
        return [o.to_model() for o in orgs]

    async def get_schedule_editors(self) -> list[User]:
        editors = await self.session.scalars(
            select(UserORM).where(
                and_(
                    UserORM.role.in_([UserRole.HELPER, UserRole.ORG]),
                    UserORM.permissions.has(
                        UserPermissionsORM.helper_can_edit_schedule.is_(True)
                    ),
                )
            )
        )
        return [e.to_model() for e in editors]

    async def update_user_settings(self, model: UserSettings) -> None:
        user_settings = await self.session.merge(UserSettingsORM.from_model(model))
        await self.session.flush([user_settings])

    async def add_points(self, user_id: UserId, points: int) -> None:
        await self.session.execute(
            update(UserORM)
            .where(UserORM.id == user_id)
            .values(points=UserORM.points + points)
        )
