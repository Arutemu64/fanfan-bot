from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from src.bot.dialogs import states

router = Router(name="start_router")


@router.message(Command("start"))
async def start_cmd(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=states.MAIN.MAIN,
        mode=StartMode.RESET_STACK,
    )


# @router.message(Command("qr"))
# async def start_native_qr_scanner(message: Message, dialog_manager: DialogManager):
#     await dialog_manager.start(
#         state=states.MAIN.QR_SCANNER,
#     )
