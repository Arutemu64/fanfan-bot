from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Cancel, Start, Url
from aiogram_dialog.widgets.text import Const

from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.ui import strings

helper_main_window = Window(
    Title(Const(strings.titles.helper_menu)),
    Const("Для волонтёров доступны следующие функции:\n"),
    Const(
        "<b>🧰 Инструменты волонтёра</b> в <code>📅 Программе</code> - "
        "Вы можете отмечать выступления на сцене как текущие, а также "
        "переносить и пропускать их.\n",
    ),
    Const(
        "<b>🔍 Найти пользователя</b> - если <code>🤳 QR-сканер</code> в главном меню "
        "не работает, вы можете найти пользователя вручную по его @никнейму или ID. "
        "Найдя пользователя, Вы можете добавить ему очков или отметить достижение "
        "как полученное",
    ),
    Start(
        state=states.UserManager.manual_user_search,
        id="user_search",
        text=Const("🔍 Найти пользователя"),
    ),
    Url(
        text=Const(strings.buttons.help_page),
        url=Const("https://fan-fan.notion.site/7234cca8ae1943b18a5bc4435342fffe"),
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.Helper.main,
)
