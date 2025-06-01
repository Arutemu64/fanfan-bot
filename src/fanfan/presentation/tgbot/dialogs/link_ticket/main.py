from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Cancel, SwitchTo
from aiogram_dialog.widgets.text import Const

from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.qr import qr_scanner_url_getter
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings

link_ticket_window = Window(
    Title(Const(strings.titles.link_ticket)),
    Const(
        "Привяжи свой билет или уникальный код и получи доступ "
        "к дополнительным возможностям:\n\n"
        "⚔️ Участию в квесте\n"
        "📣 Голосованию во внесценических номинациях\n"
        "💌 Рассылкам (для участников)\n"
        "🎁 Возможно, что-то ещё?...\n\n"
    ),
    SwitchTo(
        Const("📸 Сканировать QR-код"),
        id="qr_scan",
        state=states.LinkTicket.QR_SCAN,
        when="qr_scanner_url",
    ),
    SwitchTo(
        Const("⌨️ Ввести вручную"),
        id="manual_input",
        state=states.LinkTicket.MANUAL_INPUT,
    ),
    Cancel(Const(strings.buttons.back)),
    getter=qr_scanner_url_getter,
    state=states.LinkTicket.MAIN,
)
