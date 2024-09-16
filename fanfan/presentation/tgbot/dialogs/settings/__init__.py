from aiogram_dialog import Dialog

from .main import settings_main_window
from .set_items_per_page import items_per_page_window

dialog = Dialog(settings_main_window, items_per_page_window)
