from aiogram_dialog import Dialog

from .add_ticket import add_ticket_window
from .main import org_main_window
from .tasks import tasks_window

dialog = Dialog(
    org_main_window,
    tasks_window,
    add_ticket_window,
)
