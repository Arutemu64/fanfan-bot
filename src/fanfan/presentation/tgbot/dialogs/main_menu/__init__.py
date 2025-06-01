from aiogram_dialog import Dialog, LaunchMode

from .home import main_window

dialog = Dialog(
    main_window,
    launch_mode=LaunchMode.ROOT,
)
