from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from fanfan.application.settings.get_settings import GetSettings
from fanfan.core.enums import UserRole
from fanfan.core.models.user import FullUserDTO
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.filters import RoleFilter
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
    VOTING_CMD,
)

router = Router(name="commands_router")


@router.message(CommandStart())
async def start_cmd(
    message: Message, dialog_manager: DialogManager, state: FSMContext
) -> None:
    await state.clear()
    await dialog_manager.start(
        state=states.Main.home,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.SEND,
    )


@router.message(Command(LINK_TICKET_CMD))
async def link_ticket_cmd(
    message: Message,
    dialog_manager: DialogManager,
    user: FullUserDTO,
) -> None:
    if not user.ticket:
        await dialog_manager.start(states.Main.link_ticket)


@router.message(Command(ACTIVITIES_CMD))
async def activities_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Activities.list_activities)


@router.message(Command(SCHEDULE_CMD))
async def schedule_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Schedule.main)


@router.message(Command(NOTIFICATIONS_CMD))
async def notifications_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Schedule.subscriptions)


@router.message(Command(ACHIEVEMENTS_CMD))
async def achievements_cmd(
    message: Message,
    dialog_manager: DialogManager,
    user: FullUserDTO,
) -> None:
    if user.ticket:
        await dialog_manager.start(states.Achievements.list_achievements)


@router.message(Command(VOTING_CMD))
@inject
async def voting_cmd(
    message: Message,
    dialog_manager: DialogManager,
    get_settings: FromDishka[GetSettings],
    user: FullUserDTO,
) -> None:
    settings = await get_settings()
    if user.ticket and settings.voting_enabled:
        await dialog_manager.start(states.Voting.list_nominations)


@router.message(Command(HELPER_CMD), RoleFilter(UserRole.HELPER, UserRole.ORG))
async def helper_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Helper.main)


@router.message(Command(ORG_CMD), RoleFilter(UserRole.ORG))
async def org_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Org.main)


@router.message(Command(FEEDBACK_CMD))
async def feedback_cmd(
    message: Message,
    dialog_manager: DialogManager,
    user: FullUserDTO,
) -> None:
    if user.permissions.can_send_feedback:
        await dialog_manager.start(states.Feedback.send_feedback)


@router.message(Command(SETTINGS_CMD))
async def settings_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Settings.main)
