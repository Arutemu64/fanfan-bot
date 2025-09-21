from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from fanfan.application.quest.get_user_quest_status import GetUserQuestStatus
from fanfan.core.dto.user import FullUserDTO
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.vo.user import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.filters import RoleFilter
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
    current_user: FullUserDTO,
) -> None:
    if current_user.ticket is None:
        await dialog_manager.start(states.LinkTicket.MAIN)


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
    current_user: FullUserDTO,
    get_user_quest_status: FromDishka[GetUserQuestStatus],
) -> None:
    quest_status = await get_user_quest_status(current_user.id)
    if quest_status.can_participate_in_quest:
        await dialog_manager.start(states.Quest.MAIN)
    else:
        raise AccessDenied(quest_status.reason)


@router.message(Command(VOTING_CMD))
async def voting_cmd(
    message: Message,
    dialog_manager: DialogManager,
) -> None:
    await dialog_manager.start(states.Voting.LIST_NOMINATIONS)


@router.message(Command(STAFF_CMD), RoleFilter(UserRole.HELPER, UserRole.ORG))
async def staff_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Staff.MAIN)


@router.message(Command(SETTINGS_CMD))
async def settings_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Settings.MAIN)


@router.message(Command(MARKETPLACE_CMD))
async def marketplace_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Marketplace.LIST_MARKETS)


@router.message(Command(QR_CMD))
async def qr_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.QR.MAIN)
