from aiogram_dialog import Dialog

from .create_mailing import create_mailing_window
from .delete_mailing import delete_mailing_window
from .main import main_mailing_window

dialog = Dialog(
    main_mailing_window,
    create_mailing_window,
    delete_mailing_window,
)
