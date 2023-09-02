from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.text import Const

from src.bot.dialogs import states
from src.bot.ui import strings

helper_menu = Window(
    Const("<b>📣 Меню волонтера</b>"),
    Const(" "),
    Const(strings.menus.helper_menu_text),
    Cancel(Const(strings.buttons.back)),
    state=states.HELPER.MAIN,
)
