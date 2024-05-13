from typing import List, Union

from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

from fanfan.application.dto.user import FullUserDTO
from fanfan.common.enums import UserRole


class RoleFilter(Filter):
    def __init__(self, allowed_roles: List[UserRole]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(
        self, message: Union[Message, CallbackQuery], user: FullUserDTO
    ) -> bool:
        if isinstance(message, CallbackQuery):
            await message.answer()
        return True if user.role in self.allowed_roles else False
