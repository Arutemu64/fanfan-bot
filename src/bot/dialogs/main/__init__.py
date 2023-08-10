from aiogram_dialog import Dialog, LaunchMode

from .activities import activity
from .helper import helper_menu
from .main import main
from .org import org_menu

dialog = Dialog(activity, helper_menu, main, org_menu, launch_mode=LaunchMode.ROOT)
