from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from fanfan.core.vo.ticket import TicketId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.qr import (
    get_qr_scanner_button,
    qr_scanner_url_getter,
)
from fanfan.presentation.tgbot.dialogs.link_ticket.common import (
    manual_ticket_input_handler,
)
from fanfan.presentation.tgbot.static import strings

qr_scan_ticket_window = Window(
    Const(
        "💻 Если ты купил билет онлайн - отсканируй QR-код на билете "
        "или отправь уникальный 16-значный номер "
        "рядом со штрих-кодом."
    ),
    get_qr_scanner_button(),
    TextInput(
        id="ticket_id_input",
        type_factory=TicketId,
        on_success=manual_ticket_input_handler,
    ),
    SwitchTo(Const(strings.buttons.back), id="back", state=states.LinkTicket.MAIN),
    getter=qr_scanner_url_getter,
    state=states.LinkTicket.ONLINE_TICKET,
)
