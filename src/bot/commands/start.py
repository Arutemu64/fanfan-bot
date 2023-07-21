from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from src.bot.dialogs import states
from src.bot.ui import strings
from src.db.models import User

router = Router(name="start_router")


@router.message(Command("start"))
async def start_cmd(message: Message, user: User, dialog_manager: DialogManager):
    if user:
        await dialog_manager.start(state=states.MAIN.MAIN, mode=StartMode.RESET_STACK)
    else:
        await message.answer(strings.common.welcome)
        await dialog_manager.start(state=states.REGISTRATION.MAIN)
