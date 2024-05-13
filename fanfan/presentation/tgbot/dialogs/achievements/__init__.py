from typing import Optional

from aiogram_dialog import Dialog, DialogManager

from .constants import DATA_USER_ID
from .windows import achievements_window


async def on_start_achievements(start_data: Optional[int], manager: DialogManager):
    manager.dialog_data[DATA_USER_ID] = start_data or manager.event.from_user.id


dialog = Dialog(achievements_window, on_start=on_start_achievements)
