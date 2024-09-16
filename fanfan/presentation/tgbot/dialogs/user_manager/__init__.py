from aiogram_dialog import Dialog, DialogManager

from fanfan.presentation.tgbot import states

from .change_role import change_role_window
from .common import DATA_USER_ID
from .search_user import search_user_window
from .user_info import user_info_window


async def start_user_manager(manager: DialogManager, user_id: int) -> None:
    await manager.start(state=states.UserManager.main, data={DATA_USER_ID: user_id})


dialog = Dialog(
    user_info_window,
    search_user_window,
    change_role_window,
)
