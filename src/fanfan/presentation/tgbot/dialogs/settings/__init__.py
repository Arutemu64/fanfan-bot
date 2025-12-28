from aiogram import Router
from aiogram_dialog import Dialog

from .dev_settings import dev_settings_window
from .fest_settings import fest_settings_window
from .handlers import settings_handlers_router
from .main import settings_main_window
from .org_settings import org_settings_window
from .user_settings import items_per_page_window, user_settings_window

settings_router = Router(name="settings_router")

settings_dialog = Dialog(
    settings_main_window,
    user_settings_window,
    items_per_page_window,
    org_settings_window,
    fest_settings_window,
    dev_settings_window,
)

settings_router.include_routers(settings_handlers_router, settings_dialog)
