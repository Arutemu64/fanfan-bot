from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager

from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.filters.commands import ABOUT_CMD

activities_handlers_router = Router(name="activities_handlers_router")


@activities_handlers_router.message(Command(ABOUT_CMD))
async def activities_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Activities.LIST_ACTIVITIES)
