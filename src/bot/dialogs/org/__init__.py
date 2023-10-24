from aiogram_dialog import Dialog

from src.bot.dialogs.org.main import new_ticket_window, org_menu
from src.bot.dialogs.org.notifications import (
    confirm_notification_window,
    create_notification_window,
)

dialog = Dialog(
    org_menu, new_ticket_window, create_notification_window, confirm_notification_window
)
