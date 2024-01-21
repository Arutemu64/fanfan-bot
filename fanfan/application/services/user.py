from typing import List

from fanfan.application.dto.user import (
    CreateUserDTO,
    FullUserDTO,
    UpdateUserDTO,
    UserDTO,
)
from fanfan.application.exceptions.users import UserServiceNotFound
from fanfan.application.services.base import BaseService
from fanfan.common.enums import UserRole
from fanfan.infrastructure.db.models import User


class UserService(BaseService):
    async def create_user(self, dto: CreateUserDTO) -> FullUserDTO:
        """
        Create a new user
        """
        async with self.uow:
            user = User(id=dto.id, username=dto.username, role=dto.role)
            await self.uow.session.merge(user)
            await self.uow.commit()
            user = await self.uow.users.get_user_by_id(user.id)
            return user.to_full_dto()

    async def get_user_by_id(self, user_id: int) -> FullUserDTO:
        """
        Get user by their ID
        """
        if user := await self.uow.users.get_user_by_id(user_id):
            return user.to_full_dto()
        raise UserServiceNotFound

    async def get_user_by_username(self, username: str) -> FullUserDTO:
        """
        Get user by their username
        """
        if user := await self.uow.users.get_user_by_username(
            username.lower().replace("@", "")
        ):
            return user.to_full_dto()
        raise UserServiceNotFound

    async def get_all_by_roles(self, roles: List[UserRole]) -> List[UserDTO]:
        users = await self.uow.users.get_all_by_roles(roles)
        return [u.to_dto() for u in users]

    async def update_user(self, dto: UpdateUserDTO) -> FullUserDTO:
        """
        Update user data
        """
        async with self.uow:
            user = await self.uow.users.get_user_by_id(dto.id)
            if not user:
                raise UserServiceNotFound
            for k, v in dto.model_dump(exclude={"id"}).items():
                if v is not None:
                    user.__setattr__(k, v)
            await self.uow.commit()
            return user.to_full_dto()

    # async def open_user_manager(
    #     self,
    #     manager: DialogManager | BaseDialogManager,
    #     user_id: Optional[int] = None,
    #     username: Optional[str] = None,
    # ):
    #     if user_id:
    #         user = await self.db.users.get(user_id)
    #         if not user:
    #             raise UserServiceNotFound
    #     else:
    #         user = await self.db.users.find_by_username(username)
    #         if not user:
    #             raise UserServiceNotFound
    #     await manager.start(states.USER_MANAGER.MAIN, data=user.id)
    #
    # async def change_role(self, user_id: int, role: UserRole) -> None:
    #     user = await self.db.users.get(user_id)
    #     if not user:
    #         raise UserServiceNotFound
    #     user.user_role = role
    #     await self.db.commit()
    #     arq = await create_pool(conf.redis.get_pool_settings())
    #     await arq.enqueue_job(
    #         "send_notification",
    #         Notification(
    #             user_id=user_id,
    #             text=f"✏️ Ваша роль была изменена на <b>{user.user_role.label}</b>!",
    #         ),
    #     )
