from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager

from bot.commands.auth import auth
from bot.db.models import User

router = Router(name="common_router")


@router.message(Command("start"))
async def start_cmd(
    message: Message, state: FSMContext, user: User, dialog_manager: DialogManager
):
    await auth(message, state, user, dialog_manager)
