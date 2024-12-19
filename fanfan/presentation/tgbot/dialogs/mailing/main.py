from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Cancel, SwitchTo
from aiogram_dialog.widgets.text import Const

from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings

main_mailing_window = Window(
    Title(Const("✉️ Рассылки")),
    SwitchTo(
        Const("💌 Создать рассылку"),
        id="create_notification",
        state=states.Mailing.create_mailing,
    ),
    SwitchTo(
        Const("🔍 Найти рассылку по ID"),
        id="find_mailing_button",
        state=states.Mailing.find_mailing,
    ),
    Cancel(id="org_main_window", text=Const(strings.buttons.back)),
    state=states.Mailing.main,
)
