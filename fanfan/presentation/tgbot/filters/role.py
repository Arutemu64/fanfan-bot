from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

from fanfan.core.enums import UserRole
from fanfan.core.models.user import FullUserDTO


class RoleFilter(Filter):
    def __init__(self, *allowed_roles: UserRole) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        message: Message | CallbackQuery,
        user: FullUserDTO,
    ) -> bool:
        if isinstance(message, CallbackQuery):
            await message.answer()
        return user.role in self.allowed_roles
