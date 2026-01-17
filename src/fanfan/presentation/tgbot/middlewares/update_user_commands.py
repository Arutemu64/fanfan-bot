from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware, Bot
from aiogram.types import BotCommand, BotCommandScopeChat, TelegramObject
from dishka.integrations.aiogram import CONTAINER_NAME
from pydantic_core import to_json

from fanfan.adapters.config.models import BotFeatureFlags
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

if TYPE_CHECKING:
    from dishka import AsyncContainer


def _generate_commands_list(
    user: FullUserDTO, features: BotFeatureFlags
) -> list[BotCommand]:
    commands: list[BotCommand] = []

    if user.ticket is None:
        commands.append(LINK_TICKET_CMD)

    commands.append(START_CMD)

    if features.qr:
        commands.append(QR_CMD)
    if features.activities:
        commands.append(ABOUT_CMD)
    if features.schedule:
        commands.extend([SCHEDULE_CMD, NOTIFICATIONS_CMD])
    if features.voting:
        commands.append(VOTING_CMD)
    if features.quest:
        commands.append(QUEST_CMD)
    if features.marketplace:
        commands.append(MARKETPLACE_CMD)

    if user.role in [UserRole.HELPER, UserRole.ORG]:
        commands.append(STAFF_CMD)

    commands.append(SETTINGS_CMD)
    return commands


async def _update_bot_commands(
    bot: Bot, chat_id: int, commands_list: list[BotCommand]
) -> None:
    scope = BotCommandScopeChat(chat_id=chat_id)
    current_commands_list = await bot.get_my_commands(scope=scope)
    if to_json(commands_list) != to_json(current_commands_list):
        await bot.set_my_commands(commands_list, scope=scope)


class UpdateUserCommandsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        current_user: FullUserDTO | None = data.get(CURRENT_USER_KEY)
        if current_user:
            container: AsyncContainer = data[CONTAINER_NAME]
            bot = await container.get(Bot)
            bot_features = await container.get(BotFeatureFlags)

            commands_list = _generate_commands_list(current_user, bot_features)

            await _update_bot_commands(bot, current_user.tg_id, commands_list)

        return await handler(event, data)
