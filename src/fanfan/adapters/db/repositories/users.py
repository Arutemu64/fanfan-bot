from adaptix import Retort
from sqlalchemy import Boolean, and_, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.adapters.db.models import (
    UserORM,
)
from fanfan.adapters.db.models.permission import PermissionORM, UserPermissionORM
from fanfan.core.constants.permissions import Permissions
from fanfan.core.dto.user import UserDTO
from fanfan.core.models.user import (
    User,
    UserData,
    UserSettings,
)
from fanfan.core.vo.user import UserId, UserRole

retort = Retort()


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
        settings=retort.load(user_orm.settings, UserSettings),
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

    async def get_user_by_id(self, user_id: UserId) -> User | None:
        stmt = select(UserORM).where(UserORM.id == user_id)
        user_orm = await self.session.scalar(stmt)
        return user_orm.to_model() if user_orm else None

    async def get_user_data(
        self,
        user_id: UserId,
    ) -> UserData | None:
        stmt = (
            select(UserORM)
            .where(UserORM.id == user_id)
            .options(
                joinedload(UserORM.ticket),
            )
        )
        user_orm = await self.session.scalar(stmt)
        return _parse_user_data(user_orm) if user_orm else None

    async def save_user(self, user: User) -> User:
        user_orm = UserORM.from_model(user)
        user_orm = await self.session.merge(user_orm)
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
        stmt = select(UserORM).where(func.lower(UserORM.username) == username).limit(1)
        user_orm = await self.session.scalar(stmt)
        return _parse_user_dto(user_orm) if user_orm else None

    async def read_all_by_roles(self, *roles: UserRole) -> list[UserDTO]:
        stmt = select(UserORM).where(UserORM.role.in_(roles))
        users_orm = await self.session.scalars(stmt)
        return [_parse_user_dto(u) for u in users_orm]

    async def read_users_by_receive_all_announcements(self) -> list[UserDTO]:
        stmt = select(UserORM).where(
            cast(UserORM.settings["receive_all_announcements"].astext, Boolean)
        )
        users_orm = await self.session.scalars(stmt)
        return [_parse_user_dto(u) for u in users_orm]

    async def get_schedule_editors(self) -> list[UserDTO]:
        stmt = (
            select(UserORM)
            .join(UserPermissionORM)
            .join(PermissionORM)
            .where(PermissionORM.name == Permissions.CAN_EDIT_SCHEDULE)
        )
        editors_orm = await self.session.scalars(stmt)
        return [_parse_user_dto(e) for e in editors_orm]

    async def read_orgs_for_feedback_notification(self) -> list[UserDTO]:
        stmt = select(UserORM).where(
            and_(
                UserORM.role == UserRole.ORG,
                UserORM.settings["org_receive_feedback_notifications"].astext.cast(
                    Boolean
                ),
            )
        )
        orgs_orm = await self.session.scalars(stmt)
        return [_parse_user_dto(o) for o in orgs_orm]
