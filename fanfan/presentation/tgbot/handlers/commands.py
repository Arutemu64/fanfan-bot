from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from fanfan.presentation.tgbot.dialogs import states

router = Router(name="start_router")


@router.message(CommandStart())
async def start_cmd(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=states.MAIN.HOME,
        mode=StartMode.RESET_STACK,
    )
