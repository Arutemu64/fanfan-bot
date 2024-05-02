from aiogram_dialog import Dialog, LaunchMode

from .link_ticket import link_ticket_window
from .main import main_window

dialog = Dialog(
    main_window,
    link_ticket_window,
    launch_mode=LaunchMode.ROOT,
)
