from aiogram_dialog import Dialog, LaunchMode

from .activities import activity
from .main import main
from .schedule import schedule

dialog = Dialog(activity, main, schedule, launch_mode=LaunchMode.ROOT)
