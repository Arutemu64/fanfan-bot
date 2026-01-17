from aiogram_dialog import Dialog

from .list_activities import list_activities_window
from .view_activity import view_activity_window

activities_dialog = Dialog(
    list_activities_window,
    view_activity_window,
)
