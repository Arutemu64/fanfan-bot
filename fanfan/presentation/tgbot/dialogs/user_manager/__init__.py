from aiogram_dialog import Dialog, DialogManager

from .constants import DATA_MANAGED_USER_ID
from .windows import manual_user_search_window, role_change_window, user_manager_window


async def on_user_manager_start(start_data: int, manager: DialogManager):
    manager.dialog_data[DATA_MANAGED_USER_ID] = start_data


dialog = Dialog(
    user_manager_window,
    manual_user_search_window,
    role_change_window,
    on_start=on_user_manager_start,
)
