from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.adapters.db.models import UserORM, UserPermissionsORM, UserSettingsORM
from fanfan.core.dto.user import UserDTO
from fanfan.core.models.user import (
    User,
    UserData,
    UserId,
    UserRole,
)


def _parse_user_dto(user_orm: UserORM) -> UserDTO:
    return UserDTO(
        id=user_orm.id,
        username=user_orm.username,
        first_name=user_orm.first_name,
        last_name=user_orm.last_name,
        role=user_orm.role,
    )


def _parse_user_data(user_orm: UserORM) -> UserData:
    return UserData(
        id=UserId(user_orm.id),
        username=user_orm.username,
        first_name=user_orm.first_name,
        last_name=user_orm.last_name,
        role=UserRole(user_orm.role),
        permissions=user_orm.permissions.to_model(),
        settings=user_orm.settings.to_model(),
        ticket=user_orm.ticket.to_model() if user_orm.ticket else None,
    )


class UsersRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user(self, user: User) -> User:
        user_orm = UserORM.from_model(user)
        self.session.add(user_orm)
        await self.session.flush([user_orm])
        return user_orm.to_model()

    async def get_user_data(
        self,
        user_id: UserId,
    ) -> UserData | None:
        stmt = (
            select(UserORM)
            .where(UserORM.id == user_id)
            .options(
                joinedload(UserORM.ticket),
                joinedload(UserORM.settings),
                joinedload(UserORM.permissions),
            )
        )
        user_orm = await self.session.scalar(stmt)
        return _parse_user_data(user_orm) if user_orm else None

    async def save_user(self, user: User) -> User:
        user_orm = await self.session.merge(UserORM.from_model(user))
        await self.session.flush([user_orm])
        return user_orm.to_model()

    async def read_user_by_id(
        self,
        user_id: UserId,
    ) -> UserDTO | None:
        stmt = select(UserORM).where(UserORM.id == user_id)
        user_orm = await self.session.scalar(stmt)
        return _parse_user_dto(user_orm) if user_orm else None

    async def read_user_by_username(self, username: str) -> UserDTO | None:
        user_orm = await self.session.scalar(
            select(UserORM).where(func.lower(UserORM.username) == username).limit(1)
        )
        return _parse_user_dto(user_orm) if user_orm else None

    async def read_all_by_roles(self, *roles: UserRole) -> list[UserDTO]:
        users_orm = await self.session.scalars(
            select(UserORM).where(UserORM.role.in_(roles))
        )
        return [_parse_user_dto(u) for u in users_orm]

    async def read_users_by_receive_all_announcements(self) -> list[UserDTO]:
        users_orm = await self.session.scalars(
            select(UserORM).where(
                UserORM.settings.has(
                    UserSettingsORM.receive_all_announcements.is_(True)
                )
            )
        )
        return [_parse_user_dto(u) for u in users_orm]

    async def get_schedule_editors(self) -> list[UserDTO]:
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
        return [_parse_user_dto(e) for e in editors_orm]

    async def read_orgs_for_feedback_notification(self) -> list[UserDTO]:
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
        return [_parse_user_dto(o) for o in orgs_orm]
