from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram import inject

from fanfan.core.vo.user import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.user_manager.api import start_user_manager
from fanfan.presentation.tgbot.filters import RoleFilter
from fanfan.presentation.tgbot.filters.callbacks import ShowUserInfoCallback
from fanfan.presentation.tgbot.filters.commands import STAFF_CMD

staff_handlers_router = Router(name="staff_handlers_router")


@staff_handlers_router.message(
    Command(STAFF_CMD), RoleFilter(UserRole.HELPER, UserRole.ORG)
)
async def staff_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Staff.MAIN)


@staff_handlers_router.callback_query(ShowUserInfoCallback.filter())
@inject
async def show_user_info(
    query: CallbackQuery,
    callback_data: ShowUserInfoCallback,
    dialog_manager: DialogManager,
):
    await start_user_manager(manager=dialog_manager, user_id=callback_data.user_id)
