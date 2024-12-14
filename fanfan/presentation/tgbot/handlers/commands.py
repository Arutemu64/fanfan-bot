from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from fanfan.core.exceptions.base import AppException
from fanfan.core.models.user import FullUser, UserRole
from fanfan.core.services.access import AccessService
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.main_menu.home import SLAY_MODE
from fanfan.presentation.tgbot.filters import RoleFilter
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
    user: FullUser,
) -> None:
    if not user.ticket:
        await dialog_manager.start(states.Main.link_ticket)


@router.message(Command(ABOUT_CMD))
async def activities_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Activities.list_activities)


@router.message(Command(SCHEDULE_CMD))
async def schedule_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Schedule.main)


@router.message(Command(NOTIFICATIONS_CMD))
async def notifications_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Schedule.subscriptions)


@router.message(Command(QUEST_CMD))
@inject
async def quest_cmd(
    message: Message,
    dialog_manager: DialogManager,
    user: FullUser,
    access: FromDishka[AccessService],
) -> None:
    try:
        await access.ensure_can_participate_in_quest(user)
        await dialog_manager.start(states.Quest.main)
    except AppException:
        await dialog_manager.update(data={})


@router.message(Command(VOTING_CMD))
@inject
async def voting_cmd(
    message: Message,
    dialog_manager: DialogManager,
    user: FullUser,
    access: FromDishka[AccessService],
) -> None:
    try:
        await access.ensure_can_vote(user)
        await dialog_manager.start(states.Voting.list_nominations)
    except AppException:
        await dialog_manager.update(data={})


@router.message(Command(HELPER_CMD), RoleFilter(UserRole.HELPER, UserRole.ORG))
async def helper_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Helper.main)


@router.message(Command(ORG_CMD), RoleFilter(UserRole.ORG))
async def org_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Org.main)


@router.message(Command(FEEDBACK_CMD))
@inject
async def feedback_cmd(
    message: Message,
    dialog_manager: DialogManager,
    user: FullUser,
    access: FromDishka[AccessService],
) -> None:
    try:
        await access.ensure_can_send_feedback(user)
        await dialog_manager.start(states.Feedback.send_feedback)
    except AppException:
        await dialog_manager.update(data={})


@router.message(Command(SETTINGS_CMD))
async def settings_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Settings.main)


@router.message(Command("brat"))
async def enable_slay_mode(
    message: Message, state: FSMContext, dialog_manager: DialogManager
) -> None:
    await state.update_data({SLAY_MODE: True})
    await dialog_manager.update({})
