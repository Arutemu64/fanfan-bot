from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager

from fanfan.core.vo.user import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.filters import RoleFilter
from fanfan.presentation.tgbot.filters.commands import STAFF_CMD

staff_handlers_router = Router(name="staff_handlers_router")


@staff_handlers_router.message(
    Command(STAFF_CMD), RoleFilter(UserRole.HELPER, UserRole.ORG)
)
async def staff_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Staff.MAIN)
