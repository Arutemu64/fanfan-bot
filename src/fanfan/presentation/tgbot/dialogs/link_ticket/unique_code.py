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

manual_ticket_input_window = Window(
    Const(
        "🗝️ Если у тебя есть уникальный код от волонтёра или организатора - "
        "отсканируй его или отправь вручную.\n\n"
        "<i>Например: GWBWGS1W</i>"
    ),
    get_qr_scanner_button(),
    TextInput(
        id="ticket_id_input",
        type_factory=TicketId,
        on_success=manual_ticket_input_handler,
    ),
    SwitchTo(Const(strings.buttons.back), id="back", state=states.LinkTicket.MAIN),
    getter=qr_scanner_url_getter,
    state=states.LinkTicket.UNIQUE_CODE,
)
