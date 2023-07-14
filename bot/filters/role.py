from typing import List

from aiogram.filters import BaseFilter

from bot.db.models import User


class RoleFilter(BaseFilter):
    def __init__(self, roles: List = None) -> None:
        self.roles = roles

    async def __call__(self, event, user: User) -> bool:
        if user:
            if user.role in self.roles:
                return True
            else:
                return False
                # if type(event) is CallbackQuery:
                #     await event.answer(strings.errors.no_access, show_alert=True)
                #     return False
                # elif type(event) is Message:
                #     await event.reply(strings.errors.no_access)
                #     return False
        else:
            return False
