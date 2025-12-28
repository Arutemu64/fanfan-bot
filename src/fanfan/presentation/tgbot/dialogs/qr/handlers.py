from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager

from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.filters.commands import QR_CMD

qr_handlers_router = Router(name="qr_handlers_router")


@qr_handlers_router.message(Command(QR_CMD))
async def qr_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.QR.MAIN)
