from aiogram_dialog import Dialog

from fanfan.presentation.tgbot.dialogs.menus.org.main import (
    new_ticket_window,
    org_main_window,
)
from fanfan.presentation.tgbot.dialogs.menus.org.notifications import (
    confirm_notification_window,
    create_notification_window,
)

dialog = Dialog(
    org_main_window,
    new_ticket_window,
    create_notification_window,
    confirm_notification_window,
)
