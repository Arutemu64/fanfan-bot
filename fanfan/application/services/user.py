import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from fanfan.application.dto.user import (
    CreateUserDTO,
    FullUserDTO,
    UpdateUserDTO,
    UpdateUserSettingsDTO,
    UserDTO,
)
from fanfan.application.exceptions.users import UserAlreadyExist, UserNotFound
from fanfan.application.services.base import BaseService
from fanfan.common.enums import UserRole
from fanfan.infrastructure.db.models import User

logger = logging.getLogger(__name__)


class UserService(BaseService):
    async def create_user(self, dto: CreateUserDTO) -> FullUserDTO:
        """Create a new user"""
        async with self.uow:
            try:
                user = User(
                    id=dto.id,
                    username=dto.username,
                    role=dto.role,
                )
                self.uow.session.add(user)
                await self.uow.commit()
                logger.info(f"New user id={user.id} has registered")
                self.uow.session.expunge(user)  # To refresh relationships
                user = await self.uow.users.get_user_by_id(user.id)
                return user.to_full_dto()
            except IntegrityError:
                await self.uow.rollback()
                raise UserAlreadyExist

    async def get_user_by_id(self, user_id: int) -> FullUserDTO:
        """Get user by their ID"""
        if user := await self.uow.users.get_user_by_id(user_id):
            return user.to_full_dto()
        raise UserNotFound

    async def get_user_by_username(self, username: str) -> FullUserDTO:
        """Get user by their username"""
        if user := await self.uow.users.get_user_by_username(
            username.lower().replace("@", ""),
        ):
            return user.to_full_dto()
        raise UserNotFound

    async def get_all_by_roles(self, roles: List[UserRole]) -> List[UserDTO]:
        users = await self.uow.users.get_all_by_roles(roles)
        return [u.to_dto() for u in users]

    async def update_user(self, dto: UpdateUserDTO) -> FullUserDTO:
        """Update user data"""
        async with self.uow:
            user = await self.uow.users.get_user_by_id(dto.id)
            if not user:
                raise UserNotFound
            for k, v in dto.model_dump(exclude={"id"}, exclude_defaults=True).items():
                user.__setattr__(k, v)
            await self.uow.commit()
            return user.to_full_dto()

    async def update_user_settings(self, dto: UpdateUserSettingsDTO) -> None:
        async with self.uow:
            user = await self.uow.users.get_user_by_id(dto.user_id)
            if not user:
                raise UserNotFound
            for k, v in dto.model_dump(
                exclude={"user_id"}, exclude_defaults=True
            ).items():
                user.settings.__setattr__(k, v)
            await self.uow.commit()
