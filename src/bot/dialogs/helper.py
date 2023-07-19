from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from src.bot.dialogs import states
from src.bot.ui import strings

helper_menu = Window(
    Const("<b>📣 Меню волонтера</b>"),
    Const(" "),
    Const(strings.menus.helper_menu_text),
    Start(
        text=Const(strings.buttons.announce_mode),
        id="announce_mode",
        state=states.ANNOUNCE_MODE.MAIN,
    ),
    Start(text=Const(strings.buttons.back), id="mm", state=states.MAIN.MAIN),
    state=states.HELPER.MAIN,
)

dialog = Dialog(helper_menu)
