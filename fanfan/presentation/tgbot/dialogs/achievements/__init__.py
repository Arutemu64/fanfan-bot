from aiogram_dialog import Dialog, DialogManager

from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.achievements.list_achievements import (
    DATA_USER_ID,
    list_achievements_window,
)


async def start_achievements(
    manager: DialogManager, user_id: int | None = None, add_mode: bool = False
):
    await manager.start(
        state=states.Achievements.list_achievements,
        data={
            DATA_USER_ID: user_id or manager.event.from_user.id,
            "add_mode": add_mode,
        },
    )


dialog = Dialog(list_achievements_window)
