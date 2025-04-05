from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.models.user import UserFull, UserRole


class RoleFilter(Filter):
    def __init__(self, *allowed_roles: UserRole) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        event: Message | CallbackQuery,
        user: UserFull,
    ) -> bool:
        allowed = user.role in self.allowed_roles
        if allowed is False:
            if isinstance(event, CallbackQuery):
                await event.answer(AccessDenied.message, show_alert=True)
            else:
                await event.answer(AccessDenied.message)
        return allowed
