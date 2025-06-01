from aiogram_dialog import Dialog

from fanfan.presentation.tgbot.dialogs.link_ticket.main import link_ticket_window
from fanfan.presentation.tgbot.dialogs.link_ticket.manual_input import (
    manual_ticket_input_window,
)
from fanfan.presentation.tgbot.dialogs.link_ticket.qr_scan import (
    qr_scan_ticket_window,
)

dialog = Dialog(link_ticket_window, manual_ticket_input_window, qr_scan_ticket_window)
