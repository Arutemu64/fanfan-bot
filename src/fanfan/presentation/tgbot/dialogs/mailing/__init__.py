from aiogram_dialog import Dialog

from .create_mailing import create_mailing_window
from .find_mailing import find_mailing_window
from .main import main_mailing_window
from .view_mailing import mailing_info_window

dialog = Dialog(
    main_mailing_window,
    mailing_info_window,
    find_mailing_window,
    create_mailing_window,
)
