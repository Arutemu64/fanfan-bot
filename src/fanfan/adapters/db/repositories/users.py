from adaptix import Retort
from sqlalchemy import Boolean, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.adapters.db.models import (
    UserORM,
)
from fanfan.adapters.db.models.permission import PermissionORM, UserPermissionORM
from fanfan.core.constants.permissions import Permissions
from fanfan.core.dto.user import FullUserDTO, UserDTO, UserPermissionDTO
from fanfan.core.models.user import (
    User,
    UserSettings,
)
from fanfan.core.vo.telegram import TelegramUserId
from fanfan.core.vo.user import UserId, UserRole

retort = Retort()


def _parse_user_dto(user: UserORM) -> UserDTO:
    return UserDTO(
        id=user.id,
        tg_id=user.tg_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
    )


def _parse_full_user_dto(user: UserORM) -> FullUserDTO:
    return FullUserDTO(
        id=user.id,
        tg_id=user.tg_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        settings=retort.load(user.settings, UserSettings),
        ticket=user.ticket.to_model() if user.ticket else None,
        permissions=[
            UserPermissionDTO(
                name=p.permission.name, object_type=p.object_type, object_id=p.object_id
            )
            for p in user.permissions
        ],
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

    async def get_user_by_tg_id(self, tg_id: TelegramUserId) -> User | None:
        stmt = select(UserORM).where(UserORM.tg_id == tg_id)
        user_orm = await self.session.scalar(stmt)
        return user_orm.to_model() if user_orm else None

    async def save_user(self, user: User) -> User:
        user_orm = UserORM.from_model(user)
        user_orm = await self.session.merge(user_orm)
        await self.session.flush([user_orm])
        return user_orm.to_model()

    async def get_user_by_username(self, username: str) -> User | None:
        stmt = select(UserORM).where(func.lower(UserORM.username) == username).limit(1)
        user_orm = await self.session.scalar(stmt)
        return user_orm.to_model() if user_orm else None

    async def read_user_by_id(self, user_id: UserId) -> FullUserDTO | None:
        stmt = (
            select(UserORM)
            .where(UserORM.id == user_id)
            .options(
                joinedload(UserORM.ticket),
                joinedload(UserORM.permissions).joinedload(
                    UserPermissionORM.permission
                ),
            )
        )
        user_orm = await self.session.scalar(stmt)
        return _parse_full_user_dto(user_orm) if user_orm else None

    async def read_user_by_username(self, username: str) -> FullUserDTO | None:
        stmt = (
            select(UserORM)
            .where(func.lower(UserORM.username) == username)
            .options(
                joinedload(UserORM.ticket),
                joinedload(UserORM.permissions).joinedload(
                    UserPermissionORM.permission
                ),
            )
        )
        user_orm = await self.session.scalar(stmt)
        return _parse_full_user_dto(user_orm) if user_orm else None

    async def read_all_by_roles(self, *roles: UserRole) -> list[UserDTO]:
        stmt = select(UserORM).where(UserORM.role.in_(roles))
        users_orm = await self.session.scalars(stmt)
        return [_parse_user_dto(u) for u in users_orm]

    async def read_all_by_receive_all_announcements(self) -> list[UserDTO]:
        stmt = select(UserORM).where(
            cast(UserORM.settings["receive_all_announcements"].astext, Boolean)
        )
        users_orm = await self.session.scalars(stmt)
        return [_parse_user_dto(u) for u in users_orm]

    async def read_schedule_editors(self) -> list[UserDTO]:
        stmt = (
            select(UserORM)
            .join(UserPermissionORM)
            .join(PermissionORM)
            .where(PermissionORM.name == Permissions.CAN_MANAGE_SCHEDULE)
        )
        users_orm = await self.session.scalars(stmt)
        return [_parse_user_dto(u) for u in users_orm]
