from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from dishka.integrations.aiogram import inject

from fanfan.core.models.user import UserData
from fanfan.core.vo.user import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.filters import RoleFilter
from fanfan.presentation.tgbot.filters.commands import (
    LINK_TICKET_CMD,
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
        await dialog_manager.start(states.LinkTicket.MAIN)


@router.message(Command(VOTING_CMD))
@inject
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
