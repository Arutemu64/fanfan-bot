from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Cancel, Start
from aiogram_dialog.widgets.text import Const

from src.bot.dialogs import states
from src.bot.ui import strings

helper_menu = Window(
    Const("<b>📣 МЕНЮ ВОЛОНТЁРА</b>"),
    Const("Для волонтёров доступны следующие функции:\n"),
    Const(
        "<b>🧰 Инструменты волонтёра</b> в <code>📅 Расписании</code> - "
        "Вы можете отмечать выступления на сцене как текущие, а также "
        "переносить и пропускать их.\n"
    ),
    Const(
        "<b>🔍 Найти пользователя</b> - если <code>🤳 QR-сканер</code> в главном меню "
        "не работает, вы можете найти пользователя вручную по его @никнейму или ID. "
        "Найдя пользователя, Вы можете добавить ему очков или отметить достижение "
        "как полученное"
    ),
    Start(
        state=states.USER_MANAGER.MANUAL_USER_SEARCH,
        id="user_search",
        text=Const("🔍 Найти пользователя"),
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.HELPER.MAIN,
)

dialog = Dialog(helper_menu)
