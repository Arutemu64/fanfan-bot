from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import SwitchTo, WebApp
from aiogram_dialog.widgets.text import Const, Format

from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.qr import qr_scanner_url_getter
from fanfan.presentation.tgbot.static import strings

qr_scan_ticket_window = Window(
    Const(
        "💻 Если ты купил билет онлайн, отсканируй QR-код на билете.\n\n"
        "💵 Если ты оплатил билет на входе, отсканируй QR-код "
        "с логотипом фестиваля, предоставленный волонтёром."
    ),
    WebApp(
        Const(strings.buttons.open_qr_scanner),
        url=Format("{qr_scanner_url}"),
    ),
    SwitchTo(Const(strings.buttons.back), id="back", state=states.LinkTicket.MAIN),
    getter=qr_scanner_url_getter,
    state=states.LinkTicket.QR_SCAN,
)
