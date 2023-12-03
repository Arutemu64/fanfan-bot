from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Cancel, Start, Url
from aiogram_dialog.widgets.text import Const

from src.bot.dialogs import states
from src.bot.dialogs.widgets import Title
from src.bot.ui import strings

helper_menu = Window(
    Title(Const(strings.titles.helper_menu)),
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
    Url(
        text=Const(strings.buttons.help),
        url=Const("https://www.notion.so/arutemu64/17d4fbe591ee449caa0d631e87183a1f"),
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.HELPER.MAIN,
)

dialog = Dialog(helper_menu)
