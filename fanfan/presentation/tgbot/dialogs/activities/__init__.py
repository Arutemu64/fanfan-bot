from aiogram_dialog import Dialog

from .windows import activity_info_window, select_activity_window

dialog = Dialog(
    select_activity_window,
    activity_info_window,
)
