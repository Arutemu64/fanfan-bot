from aiogram import Router
from aiogram_dialog import Dialog

from fanfan.presentation.tgbot.dialogs.common.utils import merge_start_data

from .add_points import preview_add_points_window, set_comment_window, set_points_window
from .change_role import change_role_window
from .search_user import manual_user_search_window
from .send_message import send_message_window
from .view_user import view_user_window

user_manager_router = Router(name="user_manager_router")

user_manager_dialog = Dialog(
    view_user_window,
    manual_user_search_window,
    change_role_window,
    send_message_window,
    set_points_window,
    set_comment_window,
    preview_add_points_window,
    on_start=merge_start_data,
)

user_manager_router.include_routers(user_manager_dialog)
