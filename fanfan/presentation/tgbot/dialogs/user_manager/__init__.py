from aiogram_dialog import BaseDialogManager, Dialog, DialogManager

from fanfan.core.models.user import UserId
from fanfan.presentation.tgbot import states

from .add_points import preview_add_points_window, set_comment_window, set_points_window
from .change_role import change_role_window
from .common import DATA_USER_ID
from .search_user import manual_user_search_window
from .send_message import send_message_window
from .view_user import view_user_window


async def start_user_manager(
    manager: DialogManager | BaseDialogManager, user_id: UserId
) -> None:
    await manager.start(
        state=states.UserManager.USER_INFO, data={DATA_USER_ID: user_id}
    )


dialog = Dialog(
    view_user_window,
    manual_user_search_window,
    change_role_window,
    send_message_window,
    set_points_window,
    set_comment_window,
    preview_add_points_window,
)
