from aiogram_dialog import Dialog, LaunchMode

from .activities import activity_window
from .link_ticket import link_ticket_window
from .main import main_window
from .qr_pass import qr_pass_window

dialog = Dialog(
    main_window,
    activity_window,
    qr_pass_window,
    link_ticket_window,
    launch_mode=LaunchMode.ROOT,
)
