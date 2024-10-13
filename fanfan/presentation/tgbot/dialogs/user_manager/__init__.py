from aiogram_dialog import BaseDialogManager, Dialog, DialogManager

from fanfan.presentation.tgbot import states

from .add_points import add_points_window
from .change_role import change_role_window
from .common import DATA_USER_ID
from .search_user import manual_user_search_window
from .user_info import user_info_window


async def start_user_manager(
    manager: DialogManager | BaseDialogManager, user_id: int
) -> None:
    await manager.start(
        state=states.UserManager.user_info, data={DATA_USER_ID: user_id}
    )


dialog = Dialog(
    user_info_window,
    manual_user_search_window,
    change_role_window,
    add_points_window,
)
