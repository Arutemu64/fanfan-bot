from typing import List, Union

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from src.bot.structures import UserRole
from src.db.models import User


class RoleFilter(BaseFilter):
    def __init__(self, roles: List[UserRole]) -> None:
        self.roles = roles

    async def __call__(
        self,
        event: Union[Message, CallbackQuery],
        current_user: User,
    ) -> bool:
        if current_user:
            if current_user.role in self.roles:
                return True
            else:
                pass
        else:
            pass
        if isinstance(event, CallbackQuery):
            await event.answer(
                "У вас нет доступа к этой функции!\n"
                "Если вы застряли, перезапустите бота командой /start",
                show_alert=True,
            )
        return False
