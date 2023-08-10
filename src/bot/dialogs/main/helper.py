from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from src.bot.dialogs import states
from src.bot.ui import strings

helper_menu = Window(
    Const("<b>📣 Меню волонтера</b>"),
    Const(" "),
    Const(strings.menus.helper_menu_text),
    SwitchTo(Const(strings.buttons.back), "mm", states.MAIN.MAIN),
    state=states.MAIN.HELPER,
)
