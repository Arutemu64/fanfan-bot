from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat
from pydantic_core import to_json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.core.enums import UserRole
from fanfan.core.exceptions.users import UserNotFound
from fanfan.infrastructure.db.models import Settings, User
from fanfan.presentation.tgbot.filters.commands import (
    ACHIEVEMENTS_CMD,
    ACTIVITIES_CMD,
    FEEDBACK_CMD,
    HELPER_CMD,
    LINK_TICKET_CMD,
    NOTIFICATIONS_CMD,
    ORG_CMD,
    SCHEDULE_CMD,
    SETTINGS_CMD,
    START_CMD,
    VOTING_CMD,
)


class UpdateUserCommands:
    def __init__(
        self,
        bot: Bot,
        session: AsyncSession,
    ):
        self.bot = bot
        self.session = session

    async def __call__(self, user_id: int) -> None:
        user = await self.session.get(
            User,
            user_id,
            options=[
                joinedload(User.ticket),
                joinedload(User.permissions),
            ],
        )
        if user is None:
            raise UserNotFound
        settings = await self.session.get(Settings, 1)
        scope = BotCommandScopeChat(chat_id=user.id)
        commands: list[BotCommand] = [START_CMD]
        if user.ticket:
            commands.append(ACHIEVEMENTS_CMD)
            if settings.voting_enabled:
                commands.append(VOTING_CMD)
        else:
            commands.append(LINK_TICKET_CMD)
        commands = [*commands, ACTIVITIES_CMD, SCHEDULE_CMD, NOTIFICATIONS_CMD]
        if user.role in [UserRole.HELPER, UserRole.ORG]:
            commands.append(HELPER_CMD)
        if user.role is UserRole.ORG:
            commands.append(ORG_CMD)
        if user.permissions.can_send_feedback:
            commands.append(FEEDBACK_CMD)
        commands.append(SETTINGS_CMD)
        current_commands = await self.bot.get_my_commands(scope=scope)
        if to_json(commands) != to_json(current_commands):
            await self.bot.set_my_commands(commands, scope=scope)
