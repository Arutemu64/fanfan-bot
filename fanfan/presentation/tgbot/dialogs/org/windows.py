import operator

from aiogram import F
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Column,
    Radio,
    Start,
    SwitchTo,
    Url,
)
from aiogram_dialog.widgets.text import Case, Const, Format

from fanfan.common.enums import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.getters import (
    roles_getter,
    settings_getter,
)
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.org.constants import (
    ID_TICKET_ROLE_PICKER,
    ID_TOGGLE_VOTING_BUTTON,
)
from fanfan.presentation.tgbot.dialogs.org.getters import org_menu_getter
from fanfan.presentation.tgbot.dialogs.org.handlers import (
    add_new_ticket_handler,
    toggle_voting_handler,
)
from fanfan.presentation.tgbot.ui import strings

new_ticket_window = Window(
    Const("✔️ Отметьте роль для билета ниже и напишите его номер"),
    Column(
        Radio(
            Format("🔘 {item[1]}"),
            Format("⚪️ {item[1]}"),
            id=ID_TICKET_ROLE_PICKER,
            item_id_getter=operator.itemgetter(0),
            items="roles",
            type_factory=UserRole,
        ),
    ),
    TextInput(id="ticket_id", type_factory=str, on_success=add_new_ticket_handler),
    SwitchTo(
        state=states.ORG.MAIN,
        id="org_main_window",
        text=Const(strings.buttons.back),
    ),
    getter=roles_getter,
    state=states.ORG.ADD_NEW_TICKET,
)
org_main_window = Window(
    Title(Const(strings.titles.org_menu)),
    Url(
        text=Const("🌐 Перейти в панель организатора"),
        url=Format("{web_panel_login_link}"),
    ),
    Url(
        text=Const(strings.buttons.help_page),
        url=Const("https://fan-fan.notion.site/7234cca8ae1943b18a5bc4435342fffe"),
    ),
    Start(
        state=states.DELIVERIES.MAIN,
        id="new_notification",
        text=Const("✉️ Рассылки"),
    ),
    Start(
        state=states.USER_MANAGER.MANUAL_USER_SEARCH,
        id="user_search",
        text=Const("🔍 Найти пользователя"),
    ),
    SwitchTo(
        state=states.ORG.ADD_NEW_TICKET,
        id="new_ticket",
        text=Const("🎫 Добавить новый билет"),
    ),
    Button(
        Case(
            {
                True: Const("🔴 Выключить голосование"),
                False: Const("🟢 Включить голосование"),
            },
            selector=F["settings"].voting_enabled,
        ),
        id=ID_TOGGLE_VOTING_BUTTON,
        on_click=toggle_voting_handler,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.ORG.MAIN,
    getter=[org_menu_getter, settings_getter],
)
