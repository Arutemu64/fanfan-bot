from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from fanfan.core.exceptions.base import AppException
from fanfan.core.models.user import UserData
from fanfan.core.services.access import UserAccessValidator
from fanfan.core.vo.user import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.filters import RoleFilter
from fanfan.presentation.tgbot.filters.commands import (
    ABOUT_CMD,
    FEEDBACK_CMD,
    LINK_TICKET_CMD,
    MARKETPLACE_CMD,
    NOTIFICATIONS_CMD,
    QR_CMD,
    QUEST_CMD,
    SCHEDULE_CMD,
    SETTINGS_CMD,
    STAFF_CMD,
    VOTING_CMD,
)

router = Router(name="commands_router")


@router.message(CommandStart())
async def start_cmd(
    message: Message, dialog_manager: DialogManager, state: FSMContext
) -> None:
    await state.clear()
    await dialog_manager.start(
        state=states.Main.HOME,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.SEND,
    )


@router.message(Command(LINK_TICKET_CMD))
async def link_ticket_cmd(
    message: Message,
    dialog_manager: DialogManager,
    user: UserData,
) -> None:
    if not user.ticket:
        await dialog_manager.start(states.Main.LINK_TICKET)


@router.message(Command(ABOUT_CMD))
async def activities_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Activities.LIST_ACTIVITIES)


@router.message(Command(SCHEDULE_CMD))
async def schedule_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Schedule.MAIN)


@router.message(Command(NOTIFICATIONS_CMD))
async def notifications_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Schedule.SUBSCRIPTIONS)


@router.message(Command(QUEST_CMD))
@inject
async def quest_cmd(
    message: Message,
    dialog_manager: DialogManager,
    user: UserData,
    access: FromDishka[UserAccessValidator],
) -> None:
    try:
        access.ensure_can_participate_in_quest(user=user, ticket=user.ticket)
        await dialog_manager.start(states.Quest.MAIN)
    except AppException:
        await dialog_manager.update(data={})


@router.message(Command(VOTING_CMD))
@inject
async def voting_cmd(
    message: Message,
    dialog_manager: DialogManager,
    user: UserData,
    access: FromDishka[UserAccessValidator],
) -> None:
    try:
        await access.ensure_can_vote(user=user, ticket=user.ticket)
        await dialog_manager.start(states.Voting.LIST_NOMINATIONS)
    except AppException:
        await dialog_manager.update(data={})


@router.message(Command(STAFF_CMD), RoleFilter(UserRole.HELPER, UserRole.ORG))
async def staff_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Staff.MAIN)


@router.message(Command(FEEDBACK_CMD))
@inject
async def feedback_cmd(
    message: Message,
    dialog_manager: DialogManager,
    user: UserData,
    access: FromDishka[UserAccessValidator],
) -> None:
    try:
        access.ensure_can_send_feedback(user)
        await dialog_manager.start(states.Feedback.SEND_FEEDBACK)
    except AppException:
        await dialog_manager.update(data={})


@router.message(Command(SETTINGS_CMD))
async def settings_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Settings.MAIN)


@router.message(Command(MARKETPLACE_CMD))
async def marketplace_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Marketplace.LIST_MARKETS)


@router.message(Command(QR_CMD))
async def qr_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Main.QR_CODE)
