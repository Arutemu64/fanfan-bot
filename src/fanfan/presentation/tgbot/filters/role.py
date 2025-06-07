from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

from fanfan.core.models.user import UserData
from fanfan.core.vo.user import UserRole


class RoleFilter(Filter):
    def __init__(self, *allowed_roles: UserRole) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        event: Message | CallbackQuery,
        user: UserData,
    ) -> bool:
        allowed = user.role in self.allowed_roles
        if allowed is False:
            if isinstance(event, CallbackQuery):
                await event.answer("У вас нет доступа к этой функции", show_alert=True)
            else:
                await event.answer("У вас нет доступа к этой функции")
        return allowed
