from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat
from pydantic_core import to_json

from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.services.feedback import FeedbackService
from fanfan.core.services.quest import QuestService
from fanfan.core.services.voting import VotingService
from fanfan.core.vo.user import UserRole
from fanfan.presentation.tgbot.filters.commands import (
    ABOUT_CMD,
    FEEDBACK_CMD,
    LINK_TICKET_CMD,
    MARKETPLACE_CMD,
    NOTIFICATIONS_CMD,
    QUEST_CMD,
    SCHEDULE_CMD,
    SETTINGS_CMD,
    STAFF_CMD,
    START_CMD,
    VOTING_CMD,
)


class CMDUpdater:
    def __init__(
        self,
        bot: Bot,
        id_provider: IdProvider,
        feedback_service: FeedbackService,
        voting_service: VotingService,
        quest_service: QuestService,
    ):
        self.bot = bot
        self.id_provider = id_provider
        self.feedback_service = feedback_service
        self.voting_service = voting_service
        self.quest_service = quest_service

    async def __call__(self) -> None:
        user = await self.id_provider.get_user_data()
        scope = BotCommandScopeChat(chat_id=user.id)
        commands_list: list[BotCommand] = []

        if user.ticket is None:
            commands_list.append(LINK_TICKET_CMD)

        commands_list.append(START_CMD)
        commands_list.append(ABOUT_CMD)
        commands_list.append(SCHEDULE_CMD)
        commands_list.append(NOTIFICATIONS_CMD)

        try:
            self.quest_service.ensure_user_can_participate_in_quest(
                user=user, ticket=user.ticket
            )
            commands_list.append(QUEST_CMD)
        except AccessDenied:
            pass

        try:
            await self.voting_service.ensure_user_can_vote(
                user=user, ticket=user.ticket
            )
            commands_list.append(VOTING_CMD)
        except AccessDenied:
            pass

        commands_list.append(MARKETPLACE_CMD)

        if user.role in [UserRole.HELPER, UserRole.ORG]:
            commands_list.append(STAFF_CMD)

        try:
            self.feedback_service.ensure_user_can_send_feedback(user)
            commands_list.append(FEEDBACK_CMD)
        except AccessDenied:
            pass

        commands_list.append(SETTINGS_CMD)

        # Compare generated list to existing
        # (Telegram REALLY doesn't like frequent commands updates)
        current_commands_list = await self.bot.get_my_commands(scope=scope)
        if to_json(commands_list) != to_json(current_commands_list):
            await self.bot.set_my_commands(commands_list, scope=scope)
