from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat
from pydantic_core import to_json

from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.base import AppException
from fanfan.core.models.user import UserRole
from fanfan.core.services.access import AccessService
from fanfan.presentation.tgbot.filters.commands import (
    ABOUT_CMD,
    FEEDBACK_CMD,
    HELPER_CMD,
    LINK_TICKET_CMD,
    NOTIFICATIONS_CMD,
    ORG_CMD,
    QUEST_CMD,
    SCHEDULE_CMD,
    SETTINGS_CMD,
    START_CMD,
    VOTING_CMD,
)


class UpdateUserCommands:
    def __init__(
        self,
        bot: Bot,
        id_provider: IdProvider,
        access: AccessService,
    ):
        self.bot = bot
        self.id_provider = id_provider
        self.access = access

    async def __call__(self) -> None:
        user = await self.id_provider.get_current_user()
        scope = BotCommandScopeChat(chat_id=user.id)
        commands_list: list[BotCommand] = []

        if user.ticket is None:
            commands_list.append(LINK_TICKET_CMD)
        commands_list.append(START_CMD)
        commands_list.append(ABOUT_CMD)
        commands_list.append(SCHEDULE_CMD)
        commands_list.append(NOTIFICATIONS_CMD)

        try:
            await self.access.ensure_can_participate_in_quest(user)
            commands_list.append(QUEST_CMD)
        except AppException:
            pass

        try:
            await self.access.ensure_can_vote(user)
            commands_list.append(VOTING_CMD)
        except AppException:
            pass

        try:
            await self.access.ensure_can_send_feedback(user)
            commands_list.append(FEEDBACK_CMD)
        except AppException:
            pass

        if user.role in [UserRole.HELPER, UserRole.ORG]:
            commands_list.append(HELPER_CMD)
        if user.role is UserRole.ORG:
            commands_list.append(ORG_CMD)

        commands_list.append(SETTINGS_CMD)

        current_commands_list = await self.bot.get_my_commands(scope=scope)
        if to_json(commands_list) != to_json(current_commands_list):
            await self.bot.set_my_commands(commands_list, scope=scope)
