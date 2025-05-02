from aiogram_dialog import Dialog

from fanfan.presentation.tgbot.dialogs.staff.create_market import create_market_window
from fanfan.presentation.tgbot.dialogs.staff.create_ticket import (
    create_ticket_pick_role_window,
    create_ticket_result_window,
)
from fanfan.presentation.tgbot.dialogs.staff.main import staff_main_window

dialog = Dialog(
    staff_main_window,
    create_ticket_result_window,
    create_ticket_pick_role_window,
    create_market_window,
)
