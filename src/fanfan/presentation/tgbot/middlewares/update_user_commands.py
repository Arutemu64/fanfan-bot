from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware, Bot
from aiogram.types import BotCommand, BotCommandScopeChat, TelegramObject
from pydantic_core import to_json

from fanfan.core.dto.user import FullUserDTO
from fanfan.core.vo.user import UserRole
from fanfan.presentation.tgbot.filters.commands import (
    ABOUT_CMD,
    LINK_TICKET_CMD,
    MARKETPLACE_CMD,
    NOTIFICATIONS_CMD,
    QR_CMD,
    QUEST_CMD,
    SCHEDULE_CMD,
    SETTINGS_CMD,
    STAFF_CMD,
    START_CMD,
    VOTING_CMD,
)
from fanfan.presentation.tgbot.middlewares.load_current_user import CURRENT_USER_KEY


class UpdateUserCommandsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if data.get(CURRENT_USER_KEY):
            current_user: FullUserDTO = data[CURRENT_USER_KEY]
            bot: Bot = data["bot"]
            scope = BotCommandScopeChat(chat_id=current_user.tg_id)
            commands_list: list[BotCommand] = []

            if current_user.ticket is None:
                commands_list.append(LINK_TICKET_CMD)

            commands_list.append(START_CMD)
            commands_list.append(QR_CMD)
            commands_list.append(ABOUT_CMD)
            commands_list.append(SCHEDULE_CMD)
            commands_list.append(NOTIFICATIONS_CMD)
            commands_list.append(VOTING_CMD)
            commands_list.append(QUEST_CMD)
            commands_list.append(MARKETPLACE_CMD)

            if current_user.role in [UserRole.HELPER, UserRole.ORG]:
                commands_list.append(STAFF_CMD)

            commands_list.append(SETTINGS_CMD)

            # Compare generated list to existing
            current_commands_list = await bot.get_my_commands(scope=scope)
            if to_json(commands_list) != to_json(current_commands_list):
                await bot.set_my_commands(commands_list, scope=scope)

        return await handler(event, data)
