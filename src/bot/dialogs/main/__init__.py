from aiogram_dialog import Dialog, LaunchMode

from .achievements import achievements_window
from .activities import activity
from .main import main
from .qr_pass import qr_pass_window

dialog = Dialog(
    main,
    activity,
    achievements_window,
    qr_pass_window,
    launch_mode=LaunchMode.ROOT,
)
