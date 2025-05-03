from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.adapters.db.models import UserORM, UserPermissionsORM, UserSettingsORM
from fanfan.core.models.permissions import UserPermissions
from fanfan.core.models.user import (
    User,
    UserData,
    UserId,
    UserRole,
)
from fanfan.core.models.user_settings import UserSettings


class UsersRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _load_full(stmt: Select) -> Select:
        return stmt.options(
            joinedload(UserORM.ticket),
            joinedload(UserORM.settings),
            joinedload(UserORM.permissions),
        )

    async def add_user(self, user: User) -> User:
        user_orm = UserORM.from_model(user)
        user_orm.permissions = UserPermissionsORM.from_model(
            UserPermissions(user_id=user.id)
        )
        user_orm.settings = UserSettingsORM.from_model(UserSettings(user_id=user.id))
        self.session.add(user_orm)
        await self.session.flush([user_orm])
        return user_orm.to_model()

    async def get_user_by_id(
        self,
        user_id: UserId,
    ) -> UserData | None:
        stmt = (
            select(UserORM)
            .where(UserORM.id == user_id)
            .execution_options(populate_existing=True)
        )
        stmt = self._load_full(stmt)
        user_orm = await self.session.scalar(stmt)
        return user_orm.to_full_model() if user_orm else None

    async def get_user_by_username(self, username: str) -> User | None:
        user_orm = await self.session.scalar(
            select(UserORM).where(func.lower(UserORM.username) == username).limit(1)
        )
        return user_orm.to_model() if user_orm else None

    async def get_all_by_roles(self, *roles: UserRole) -> list[User]:
        users_orm = await self.session.scalars(
            select(UserORM).where(UserORM.role.in_(roles))
        )
        return [u.to_model() for u in users_orm]

    async def get_users_by_receive_all_announcements(self) -> list[User]:
        users_orm = await self.session.scalars(
            select(UserORM).where(
                UserORM.settings.has(
                    UserSettingsORM.receive_all_announcements.is_(True)
                )
            )
        )
        return [u.to_model() for u in users_orm]

    async def get_orgs_for_feedback_notification(self) -> list[User]:
        orgs_orm = await self.session.scalars(
            select(UserORM).where(
                and_(
                    UserORM.role == UserRole.ORG,
                    UserORM.settings.has(
                        UserSettingsORM.org_receive_feedback_notifications.is_(True)
                    ),
                )
            )
        )
        return [o.to_model() for o in orgs_orm]

    async def get_schedule_editors(self) -> list[User]:
        editors_orm = await self.session.scalars(
            select(UserORM).where(
                and_(
                    UserORM.role.in_([UserRole.HELPER, UserRole.ORG]),
                    UserORM.permissions.has(
                        UserPermissionsORM.can_edit_schedule.is_(True)
                    ),
                )
            )
        )
        return [e.to_model() for e in editors_orm]

    async def save_user(self, user: User) -> User:
        user_orm = await self.session.merge(UserORM.from_model(user))
        await self.session.flush([user_orm])
        return user_orm.to_model()

    async def save_user_settings(self, user_settings: UserSettings) -> None:
        user_settings_orm = await self.session.merge(
            UserSettingsORM.from_model(user_settings)
        )
        await self.session.flush([user_settings_orm])
