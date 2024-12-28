from aiogram_dialog import Dialog

from .add_ticket import add_ticket_window
from .main import org_main_window

dialog = Dialog(
    org_main_window,
    add_ticket_window,
)
