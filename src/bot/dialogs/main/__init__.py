from typing import Any

from aiogram_dialog import Dialog, DialogManager, LaunchMode, StartMode

from src.bot.dialogs import states
from src.bot.ui import strings
from src.db import Database

from .activities import activity
from .main import main


async def on_start_main(start_data: Any, manager: DialogManager):
    db: Database = manager.middleware_data["db"]

    # Проверка регистрации
    user = await db.user.get(manager.event.from_user.id)
    if user:
        if user.username != manager.event.from_user.username:
            user.username = manager.event.from_user.username
            await db.session.commit()
    else:
        await manager.event.answer(strings.common.welcome)
        await manager.start(states.REGISTRATION.MAIN, mode=StartMode.RESET_STACK)


dialog = Dialog(activity, main, launch_mode=LaunchMode.ROOT, on_start=on_start_main)
