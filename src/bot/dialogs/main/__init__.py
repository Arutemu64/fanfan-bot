from aiogram_dialog import Dialog, LaunchMode

from .achievements import achievements_window
from .activities import activity_window
from .main import main_window
from .qr_pass import qr_pass_window

dialog = Dialog(
    main_window,
    activity_window,
    achievements_window,
    qr_pass_window,
    launch_mode=LaunchMode.ROOT,
)
