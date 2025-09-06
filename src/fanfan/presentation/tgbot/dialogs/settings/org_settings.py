from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings

org_settings_window = Window(
    Title(Const(strings.titles.org_settings)),
    SwitchTo(Const(strings.buttons.back), state=states.Settings.MAIN, id="back"),
    state=states.Settings.ORG_SETTINGS,
)
