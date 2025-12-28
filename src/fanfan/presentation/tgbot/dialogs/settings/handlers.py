from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager

from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.filters.commands import SETTINGS_CMD

settings_handlers_router = Router(name="settings_handlers_router")


@settings_handlers_router.message(Command(SETTINGS_CMD))
async def settings_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Settings.MAIN)
