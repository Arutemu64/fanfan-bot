from aiogram_dialog import Dialog

from fanfan.presentation.tgbot.dialogs.common.utils import merge_start_data

from .create_mailing import create_mailing_window
from .find_mailing import find_mailing_window
from .main import main_mailing_window
from .view_mailing import mailing_info_window

mailing_dialog = Dialog(
    main_mailing_window,
    mailing_info_window,
    find_mailing_window,
    create_mailing_window,
    on_start=merge_start_data,
)
