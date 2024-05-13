from aiogram_dialog import Dialog

from .windows import new_ticket_window, org_main_window

dialog = Dialog(
    org_main_window,
    new_ticket_window,
)
