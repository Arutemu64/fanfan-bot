from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Cancel, SwitchTo
from aiogram_dialog.widgets.text import Const

from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings

link_ticket_window = Window(
    Title(Const(strings.titles.link_ticket)),
    Const(
        "Привяжи свой билет или уникальный код и получи доступ "
        "к дополнительным возможностям:\n\n"
        "📣 Голосованию во внесценических номинациях\n"
        "💌 Рассылкам (для участников)\n"
        "🤩 Возможно, что-то ещё?...\n\n"
    ),
    SwitchTo(
        Const("💻 Я купил билет онлайн"),
        id="online_ticket",
        state=states.LinkTicket.ONLINE_TICKET,
    ),
    SwitchTo(
        Const("🗝️ У меня есть уникальный код"),
        id="unique_key",
        state=states.LinkTicket.UNIQUE_CODE,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.LinkTicket.MAIN,
)
