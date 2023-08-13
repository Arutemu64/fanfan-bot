from aiogram_dialog import Dialog, LaunchMode

from .activities import activity
from .helper import helper_menu
from .main import main

dialog = Dialog(activity, helper_menu, main, launch_mode=LaunchMode.ROOT)
