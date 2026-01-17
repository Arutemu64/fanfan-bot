from aiogram_dialog import Dialog

from fanfan.presentation.tgbot.dialogs.link_ticket.main import link_ticket_window
from fanfan.presentation.tgbot.dialogs.link_ticket.online_ticket import (
    qr_scan_ticket_window,
)
from fanfan.presentation.tgbot.dialogs.link_ticket.unique_code import (
    manual_ticket_input_window,
)

link_ticket_dialog = Dialog(
    link_ticket_window, manual_ticket_input_window, qr_scan_ticket_window
)
