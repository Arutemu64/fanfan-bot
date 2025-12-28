from aiogram import Router
from aiogram_dialog import Dialog

from .handlers import activities_handlers_router
from .list_activities import list_activities_window
from .view_activity import view_activity_window

activities_router = Router(name="activities_router")

activities_dialog = Dialog(
    list_activities_window,
    view_activity_window,
)

activities_router.include_routers(activities_handlers_router, activities_dialog)
