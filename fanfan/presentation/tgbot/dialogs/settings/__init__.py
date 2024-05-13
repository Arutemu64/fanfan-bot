from aiogram_dialog import Dialog

from .windows import items_per_page_window, settings_main_window

dialog = Dialog(settings_main_window, items_per_page_window)
