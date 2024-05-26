import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from fanfan.application.dto.user import (
    CreateUserDTO,
    FullUserDTO,
    UpdateUserDTO,
    UserDTO,
)
from fanfan.application.exceptions.users import UserAlreadyExist, UserNotFound
from fanfan.application.services.base import BaseService
from fanfan.common.enums import UserRole

logger = logging.getLogger(__name__)


class UserService(BaseService):
    async def create_user(self, dto: CreateUserDTO) -> UserDTO:
        """Create a new user"""
        async with self.uow:
            try:
                user = await self.uow.users.add_user(dto)
                await self.uow.commit()
                logger.info(f"New user id={user.id} has registered")
                return user
            except IntegrityError:
                await self.uow.rollback()
                raise UserAlreadyExist

    async def get_user_by_id(self, user_id: int) -> FullUserDTO:
        """Get user by their ID"""
        if user := await self.uow.users.get_user_by_id(user_id):
            return user
        raise UserNotFound

    async def get_user_by_username(self, username: str) -> FullUserDTO:
        """Get user by their username"""
        if user := await self.uow.users.get_user_by_username(
            username.lower().replace("@", ""),
        ):
            return user
        raise UserNotFound

    async def get_all_by_roles(self, roles: List[UserRole]) -> List[UserDTO]:
        return await self.uow.users.get_all_by_roles(roles)

    async def update_user(self, dto: UpdateUserDTO) -> None:
        """Update user data"""
        async with self.uow:
            await self.uow.users.update_user(dto)
            await self.uow.commit()
            return
