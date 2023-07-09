from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.db.models import User
from bot.ui import strings


# данная мидлварь пробрасывает в хендлеры роль пользователя из БД
class RoleMiddleware(BaseMiddleware):
    """
    This class is used for getting user role from database
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        if get_flag(data, "bypass_verification"):
            return await handler(event, data)
        user: User = data["user"]
        if user is None:
            if type(event) is CallbackQuery:
                await event.answer(strings.errors.no_access, show_alert=True)
            elif type(event) is Message:
                await event.reply(strings.errors.no_access)
            return
        allowed_roles = get_flag(data, "allowed_roles")
        if allowed_roles:
            if user.role in allowed_roles:
                return await handler(event, data)
            else:
                if type(event) is CallbackQuery:
                    await event.answer(strings.errors.no_access, show_alert=True)
                elif type(event) is Message:
                    await event.reply(strings.errors.no_access)
                return
        else:
            return await handler(event, data)
