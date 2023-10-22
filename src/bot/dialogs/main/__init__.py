from typing import Any

from aiogram_dialog import Dialog, DialogManager, LaunchMode, StartMode

from src.bot.dialogs import states

from .achievements import achievements_window
from .activities import activity
from .main import main
from .qr_pass import qr_pass_window


async def on_start_main(start_data: Any, manager: DialogManager):
    if not manager.middleware_data["current_user"]:
        await manager.event.answer(
            "Тебя приветствует (тестовый) бот Нижегородского "
            "фестиваля анимации и фантастики FAN-FAN! 👋"
        )
        await manager.start(states.REGISTRATION.MAIN, mode=StartMode.RESET_STACK)


dialog = Dialog(
    main,
    activity,
    achievements_window,
    qr_pass_window,
    launch_mode=LaunchMode.ROOT,
    on_start=on_start_main,
)
