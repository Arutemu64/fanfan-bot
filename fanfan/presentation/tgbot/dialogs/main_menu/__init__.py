from aiogram_dialog import Dialog, LaunchMode

from .home import main_window
from .link_ticket import link_ticket_window

dialog = Dialog(
    main_window,
    link_ticket_window,
    launch_mode=LaunchMode.ROOT,
)
