from aiogram_dialog import Dialog

from .add_new_ticket import new_ticket_window
from .main import org_menu
from .user_editor import ask_username_window, changing_role_window, user_editor

dialog = Dialog(
    org_menu, new_ticket_window, ask_username_window, user_editor, changing_role_window
)
