from aiogram_dialog import Dialog, LaunchMode

from .home import main_window
from .image_maker import image_maker_window

dialog = Dialog(
    main_window,
    image_maker_window,
    launch_mode=LaunchMode.ROOT,
)
