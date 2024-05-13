from aiogram_dialog import Dialog, LaunchMode

from .windows import link_ticket_window, main_window

dialog = Dialog(
    main_window,
    link_ticket_window,
    launch_mode=LaunchMode.ROOT,
)
