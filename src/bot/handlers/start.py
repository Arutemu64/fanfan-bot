from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from src.bot.dialogs import states
from src.bot.structures import UserRole
from src.bot.ui import strings
from src.config import conf
from src.db import Database
from src.db.models import User

router = Router(name="start_router")


@router.message(Command("start"))
async def start_cmd(
    message: Message, user: User, dialog_manager: DialogManager, db: Database
):
    if user:
        await dialog_manager.start(state=states.MAIN.MAIN, mode=StartMode.RESET_STACK)
    else:
        if message.from_user.username.lower() in conf.bot.admin_list:
            await message.answer(
                "Ваш никнейм найден в списке администраторов, добро пожаловать!"
            )
            user = await db.user.new(
                id=message.from_user.id,
                username=message.from_user.username.lower(),
                role=UserRole.ORG,
            )
            await db.session.commit()
            dialog_manager.middleware_data["user"] = user
            await dialog_manager.start(
                state=states.MAIN.MAIN, mode=StartMode.RESET_STACK
            )
        else:
            await message.answer(strings.common.welcome)
            await dialog_manager.start(
                state=states.REGISTRATION.MAIN, mode=StartMode.RESET_STACK
            )
