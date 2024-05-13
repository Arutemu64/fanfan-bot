from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Counter, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, Jinja

from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.ui import strings

from ..common.getters import current_user_getter, settings_getter
from .constants import ID_ITEMS_PER_PAGE_INPUT
from .handlers import items_per_page_handler, update_counter_value_handler

items_per_page_window = Window(
    Const(
        "🔢 <b>Укажите, сколько выступлений/участников выводить "
        "на одной странице</b> <i>(от 3 до 10)</i>",
    ),
    Counter(
        id=ID_ITEMS_PER_PAGE_INPUT,
        plus=Const("➕"),
        minus=Const("➖"),
        min_value=3,
        max_value=10,
    ),
    Button(
        text=Const("💾 Сохранить"),
        id="save_items_per_page",
        on_click=items_per_page_handler,
    ),
    state=states.SETTINGS.SET_ITEMS_PER_PAGE,
)
settings_main_window = Window(
    Title(Const(strings.titles.settings)),
    Format("<b>Никнейм:</b> {current_user.username}"),
    Format("<b>ID:</b> {current_user.id}"),
    Jinja(
        """<b>Билет:</b> """
        """{% if current_user.ticket %}"""
        """{{current_user.ticket.id}}{% else %}не привязан{% endif %}"""
    ),
    Format("<b>Роль:</b> {current_user.role.label}"),
    SwitchTo(
        text=Format(
            "🔢 Количество элементов на странице: {current_user.settings.items_per_page}"
        ),
        id="set_items_per_page_button",
        on_click=update_counter_value_handler,
        state=states.SETTINGS.SET_ITEMS_PER_PAGE,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.SETTINGS.MAIN,
    getter=[current_user_getter, settings_getter],
)
