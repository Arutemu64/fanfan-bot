from typing import Any

from aiogram_dialog import Dialog, DialogManager, LaunchMode, StartMode

from src.bot.dialogs import states
from src.db import Database

from .achievements import achievements_window
from .activities import activity
from .main import main
from .qr_pass import qr_pass_window
from .qr_scanner import qr_scanner_window


async def on_start_main(start_data: Any, manager: DialogManager):
    db: Database = manager.middleware_data["db"]

    # Проверка регистрации
    if not await db.user.exists(user_id=manager.event.from_user.id):
        await manager.event.answer(
            "Тебя приветствует (тестовый) бот Нижегородского "
            "фестиваля анимации и фантастики FAN-FAN! 👋"
        )
        await manager.start(states.REGISTRATION.MAIN, mode=StartMode.RESET_STACK)


dialog = Dialog(
    main,
    activity,
    achievements_window,
    qr_scanner_window,
    qr_pass_window,
    launch_mode=LaunchMode.ROOT,
    on_start=on_start_main,
)
