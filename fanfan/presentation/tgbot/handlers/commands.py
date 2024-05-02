from typing import List

from aiogram import Bot, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import BotCommand, BotCommandScopeChat, Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from pydantic_core import to_json

from fanfan.application.dto.settings import SettingsDTO
from fanfan.application.dto.user import FullUserDTO
from fanfan.application.holder import AppHolder
from fanfan.common.enums import UserRole
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.filters import RoleFilter
from fanfan.presentation.tgbot.ui.strings import titles

START_CMD = BotCommand(command="start", description=titles.main_menu)
LINK_TICKET_CMD = BotCommand(command="ticket", description=titles.link_ticket)
ACTIVITIES_CMD = BotCommand(command="activities", description=titles.activities)
SCHEDULE_CMD = BotCommand(command="schedule", description=titles.schedule)
NOTIFICATIONS_CMD = BotCommand(
    command="notifications", description=titles.notifications
)
ACHIEVEMENTS_CMD = BotCommand(command="achievements", description=titles.achievements)
VOTING_CMD = BotCommand(command="voting", description=titles.voting)
HELPER_CMD = BotCommand(command="helper", description=titles.helper_menu)
ORG_CMD = BotCommand(command="org", description=titles.org_menu)
FEEDBACK_CMD = BotCommand(command="feedback", description=titles.feedback)
SETTINGS_CMD = BotCommand(command="settings", description=titles.settings)

router = Router(name="commands_router")


@router.message(CommandStart())
async def start_cmd(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=states.MAIN.HOME, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND
    )


@router.message(Command(LINK_TICKET_CMD))
async def link_ticket_cmd(
    message: Message, dialog_manager: DialogManager, user: FullUserDTO
):
    if not user.ticket:
        await dialog_manager.start(states.MAIN.LINK_TICKET)


@router.message(Command(ACTIVITIES_CMD))
async def activities_cmd(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(states.ACTIVITIES.SELECT_ACTIVITY)


@router.message(Command(SCHEDULE_CMD))
async def schedule_cmd(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(states.SCHEDULE.MAIN)


@router.message(Command(NOTIFICATIONS_CMD))
async def notifications_cmd(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(states.SUBSCRIPTIONS.MAIN)


@router.message(Command(ACHIEVEMENTS_CMD))
async def achievements_cmd(
    message: Message, dialog_manager: DialogManager, user: FullUserDTO
):
    if user.ticket:
        await dialog_manager.start(states.ACHIEVEMENTS.MAIN)


@router.message(Command(VOTING_CMD))
async def voting_cmd(
    message: Message, dialog_manager: DialogManager, user: FullUserDTO, app: AppHolder
):
    settings = await app.settings.get_settings()
    if user.ticket and settings.voting_enabled:
        await dialog_manager.start(states.VOTING.SELECT_NOMINATION)


@router.message(Command(HELPER_CMD), RoleFilter([UserRole.HELPER, UserRole.ORG]))
async def helper_cmd(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(states.HELPER.MAIN)


@router.message(Command(ORG_CMD), RoleFilter([UserRole.ORG]))
async def org_cmd(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(states.ORG.MAIN)


@router.message(Command(FEEDBACK_CMD))
async def feedback_cmd(
    message: Message, dialog_manager: DialogManager, user: FullUserDTO
):
    if user.permissions.can_send_feedback:
        await dialog_manager.start(states.FEEDBACK.MAIN)


@router.message(Command(SETTINGS_CMD))
async def settings_cmd(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(states.SETTINGS.MAIN)


async def update_user_commands(
    bot: Bot, user: FullUserDTO, settings: SettingsDTO
) -> None:
    scope = BotCommandScopeChat(chat_id=user.id)
    commands: List[BotCommand] = [START_CMD]
    if user.ticket:
        commands.append(ACHIEVEMENTS_CMD)
        if settings.voting_enabled:
            commands.append(VOTING_CMD)
    else:
        commands.append(LINK_TICKET_CMD)
    commands = commands + [ACTIVITIES_CMD, SCHEDULE_CMD, NOTIFICATIONS_CMD]
    if user.role in [UserRole.HELPER, UserRole.ORG]:
        commands.append(HELPER_CMD)
    if user.role is UserRole.ORG:
        commands.append(ORG_CMD)
    if user.permissions.can_send_feedback:
        commands.append(FEEDBACK_CMD)
    commands.append(SETTINGS_CMD)
    current_commands = await bot.get_my_commands(scope=scope)
    if to_json(commands) != to_json(current_commands):
        await bot.set_my_commands(commands, scope=scope)
