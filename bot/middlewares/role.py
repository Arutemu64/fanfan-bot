from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from aiogram.dispatcher.flags import get_flag

from bot.ui import strings
from bot.db.models import User


# данная мидлварь пробрасывает в хендлеры роль пользователя из БД
class RoleMiddleware(BaseMiddleware):
    """
    This class is used for getting user role from database
    """

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        if type(event) is Message:
            if event.text == '/start' or event.text == '/menu':
                return await handler(event, data)
        allowed_roles = get_flag(data, 'allowed_roles')
        try:
            user: User = data["user"]
        except KeyError:
            if type(event) is CallbackQuery:
                await event.answer(strings.no_access, show_alert=True)
            elif type(event) is Message:
                await event.reply(strings.no_access)
            return
        if user is None:
            if type(event) is CallbackQuery:
                await event.answer(strings.no_access, show_alert=True)
            elif type(event) is Message:
                await event.reply(strings.no_access)
            return
        if allowed_roles:
            if user.role in allowed_roles:
                return await handler(event, data)
            else:
                if type(event) is CallbackQuery:
                    await event.answer(strings.no_access, show_alert=True)
                elif type(event) is Message:
                    await event.reply(strings.no_access)
                return
        else:
            return await handler(event, data)
