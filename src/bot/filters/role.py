from typing import List

from aiogram.filters import BaseFilter

from src.db.models import User


class RoleFilter(BaseFilter):
    def __init__(self, roles: List = None) -> None:
        self.roles = roles

    async def __call__(self, event, user: User) -> bool:
        if user:
            if user.role in self.roles:
                return True
            else:
                # if type(event) is CallbackQuery:
                #     await event.answer(strings.errors.no_access, show_alert=True)
                # elif type(event) is Message:
                #     await event.reply(strings.errors.no_access)
                return False
        else:
            return False
