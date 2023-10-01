from typing import List, Optional, Union

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from src.db import Database


class RoleFilter(BaseFilter):
    def __init__(self, roles: Optional[List] = None) -> None:
        self.roles = roles

    async def __call__(
        self, event: Union[Message, CallbackQuery], db: Database
    ) -> bool:
        user_role = await db.user.get_role(event.from_user.id)
        if user_role in self.roles:
            return True
        else:
            if isinstance(event, CallbackQuery):
                await event.answer(
                    "У вас нет доступа к этой функции!\n"
                    "Если вы застряли, перезапустите бота командой /start",
                    show_alert=True,
                )
            return False
