from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager

from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.filters.commands import MARKETPLACE_CMD

marketplace_handlers_router = Router(name="marketplace_handlers_router")


@marketplace_handlers_router.message(Command(MARKETPLACE_CMD))
async def marketplace_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Marketplace.LIST_MARKETS)
